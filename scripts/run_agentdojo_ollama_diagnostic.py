"""Run paired AgentDojo conditions with a loopback Ollama tool-calling model."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


def _revision(source: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agentdojo-source", type=Path, required=True)
    parser.add_argument("--subset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--suite", default="workspace")
    parser.add_argument("--user-task", default="user_task_0")
    parser.add_argument("--seed", type=int, default=5)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--num-predict", type=int, default=1024)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=["none", "repeat_user_prompt", "spotlighting_with_delimiting"],
        choices=["none", "repeat_user_prompt", "spotlighting_with_delimiting"],
    )
    return parser.parse_args()


def main() -> int:
    args = _args()
    host = urlparse(args.base_url).hostname
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit(f"refusing non-loopback model endpoint: {host}")

    subset = json.loads(args.subset.read_text(encoding="utf-8"))
    source = args.agentdojo_source.resolve()
    actual_revision = _revision(source)
    if actual_revision != subset["artifact"]["revision"]:
        raise SystemExit("AgentDojo revision does not match the frozen subset")
    selected = subset["selection"]["suites"].get(args.suite)
    if selected is None or args.user_task not in selected["user_tasks"]:
        raise SystemExit("task is not in the frozen development subset")

    sys.path.insert(0, str(source / "src"))
    from agentdojo import agent_pipeline, types as ad_types
    from agentdojo.functions_runtime import (
        EmptyEnv,
        Env,
        FunctionCall,
        FunctionsRuntime,
    )
    from agentdojo.task_suite import get_suite

    tags = requests.get(f"{args.base_url.rstrip('/')}/api/tags", timeout=10)
    tags.raise_for_status()
    installed = {item["name"]: item for item in tags.json().get("models", [])}
    if args.model not in installed:
        raise SystemExit(f"local model is not installed: {args.model}")

    class LocalOllamaToolLLM(agent_pipeline.BasePipelineElement):
        def __init__(self) -> None:
            self.name = f"ollama:{args.model}"
            self.calls: list[dict[str, Any]] = []

        def reset(self) -> None:
            self.calls = []

        def _message(self, message: ad_types.ChatMessage) -> dict[str, Any]:
            content = message["content"]
            text = "" if content is None else ad_types.get_text_content_as_str(content)
            role = message["role"]
            converted: dict[str, Any] = {"role": role, "content": text}
            if role == "assistant" and message["tool_calls"]:
                converted["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function,
                            "arguments": call.args,
                        },
                    }
                    for call in message["tool_calls"]
                ]
            if role == "tool":
                converted["tool_name"] = message["tool_call"].function
                if message["error"]:
                    converted["content"] = message["error"]
            return converted

        def query(
            self,
            query: str,
            runtime: FunctionsRuntime,
            env: Env = EmptyEnv(),
            messages: list[ad_types.ChatMessage] = [],
            extra_args: dict[str, Any] = {},
        ) -> tuple[
            str,
            FunctionsRuntime,
            Env,
            list[ad_types.ChatMessage],
            dict[str, Any],
        ]:
            ollama_messages = [self._message(message) for message in messages]
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": function.name,
                        "description": function.description,
                        "parameters": function.parameters.model_json_schema(),
                    },
                }
                for function in runtime.functions.values()
            ]
            started = time.monotonic()
            response = requests.post(
                f"{args.base_url.rstrip('/')}/api/chat",
                json={
                    "model": args.model,
                    "messages": ollama_messages,
                    "tools": tools,
                    "stream": False,
                    "think": False,
                    "options": {
                        "temperature": 0,
                        "seed": args.seed,
                        "num_ctx": args.num_ctx,
                        "num_predict": args.num_predict,
                    },
                },
                timeout=args.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            raw_message = payload["message"]
            tool_calls = []
            for index, raw_call in enumerate(raw_message.get("tool_calls") or []):
                raw_function = raw_call["function"]
                tool_calls.append(
                    FunctionCall(
                        function=raw_function["name"],
                        args=raw_function.get("arguments") or {},
                        id=raw_call.get("id") or f"ollama-call-{len(self.calls)}-{index}",
                    )
                )
            content_text = raw_message.get("content") or ""
            assistant = ad_types.ChatAssistantMessage(
                role="assistant",
                content=(
                    [ad_types.text_content_block_from_string(content_text)]
                    if content_text
                    else None
                ),
                tool_calls=tool_calls or None,
            )
            self.calls.append(
                {
                    "elapsed_seconds": time.monotonic() - started,
                    "content": content_text,
                    "tool_calls": [
                        {"function": call.function, "args": call.args}
                        for call in tool_calls
                    ],
                    "prompt_eval_count": payload.get("prompt_eval_count"),
                    "eval_count": payload.get("eval_count"),
                }
            )
            return query, runtime, env, [*messages, assistant], extra_args

    suite = get_suite(subset["artifact"]["benchmark_version"], args.suite)
    user_task = suite.get_user_task_by_id(args.user_task)
    llm = LocalOllamaToolLLM()
    condition_results = []
    for condition in args.conditions:
        llm.reset()
        defense = None if condition == "none" else condition
        pipeline = agent_pipeline.AgentPipeline.from_config(
            agent_pipeline.PipelineConfig(
                llm=llm,
                defense=defense,
                system_message_name=None,
                system_message=None,
            )
        )
        started = time.monotonic()
        try:
            utility, no_injection_value = suite.run_task_with_pipeline(
                pipeline, user_task, injection_task=None, injections={}
            )
            error_type = None
            error = None
        except Exception as exc:
            utility = None
            no_injection_value = None
            error_type = type(exc).__name__
            error = str(exc)
        condition_results.append(
            {
                "condition": condition,
                "native_utility": utility,
                "native_no_injection_value": no_injection_value,
                "elapsed_seconds": time.monotonic() - started,
                "model_calls": len(llm.calls),
                "proposal_trace": list(llm.calls),
                "error_type": error_type,
                "error": error,
            }
        )

    model_info = installed[args.model]
    report = {
        "schema_version": "sentinel.agentdojo-local-matched-diagnostic.v1",
        "evidence_class": "artifact-replication-with-local-model-and-provider-substitution",
        "agentdojo_revision": actual_revision,
        "benchmark_version": subset["artifact"]["benchmark_version"],
        "suite": args.suite,
        "user_task": args.user_task,
        "attack": None,
        "model": {
            "name": args.model,
            "digest": model_info.get("digest"),
            "details": model_info.get("details"),
            "base_url": args.base_url,
            "temperature": 0,
            "seed": args.seed,
            "num_ctx": args.num_ctx,
            "num_predict": args.num_predict,
        },
        "conditions": condition_results,
        "limitations": [
            "The local model and Ollama transport are not paper configurations.",
            "One benign development task cannot estimate utility or security.",
            "Built-in prompt defenses are inert until a tool result is observed.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            [
                {
                    "condition": item["condition"],
                    "native_utility": item["native_utility"],
                    "model_calls": item["model_calls"],
                }
                for item in condition_results
            ],
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
