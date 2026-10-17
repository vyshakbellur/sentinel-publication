"""Generate manuscript figures from immutable SENTINEL evidence reports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).parents[1]
FIGURES = ROOT / "paper" / "figures"
REPORTS = ROOT / "_workloads" / "reproduction"
FIGURE_DATA = ROOT / "paper" / "data" / "development_figure_data.json"

COLORS = {
    "untrusted": "#9ca3af",
    "boundary": "#2563eb",
    "environment": "#d97706",
    "oracle": "#059669",
    "unsafe": "#b91c1c",
    "neutral": "#4b5563",
    "missing": "#d1d5db",
}

mpl.rcParams["svg.hashsalt"] = "sentinel-paper-v1"


def load(path: str) -> dict:
    snapshot = json.loads(FIGURE_DATA.read_text())
    report = snapshot["reports"][path]
    local_source = REPORTS / path / "report.json"
    if local_source.exists():
        digest = hashlib.sha256(local_source.read_bytes()).hexdigest()
        if digest != report["source_sha256"]:
            raise ValueError(f"source report digest mismatch: {path}")
    return report


def save(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    svg = FIGURES / f"{stem}.svg"
    fig.savefig(svg, bbox_inches="tight", metadata={"Date": None})
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n"
    )
    fig.savefig(
        FIGURES / f"{stem}.pdf",
        bbox_inches="tight",
        metadata={"CreationDate": None, "ModDate": None},
    )
    fig.savefig(FIGURES / f"{stem}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def architecture() -> None:
    fig, ax = plt.subplots(figsize=(12.4, 5.8))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    nodes = [
        (0.3, 3.5, 1.65, "Untrusted request\n+ service data", "untrusted"),
        (2.15, 3.5, 1.45, "Probabilistic\nplanner", "untrusted"),
        (3.8, 3.5, 1.35, "Protocol\nadapter", "boundary"),
        (5.35, 3.5, 1.45, "Trusted tuple\nbinder", "boundary"),
        (7.0, 3.5, 1.55, "Policy + workflow\nscheduler", "boundary"),
        (8.75, 3.5, 1.45, "Credential /\neffect broker", "boundary"),
        (10.4, 3.5, 1.65, "Service or\ntool environment", "environment"),
    ]
    centers = []
    for x, y, width, label, group in nodes:
        box = FancyBboxPatch(
            (x, y),
            width,
            0.9,
            boxstyle="round,pad=0.08,rounding_size=0.08",
            linewidth=1.2,
            edgecolor=COLORS[group],
            facecolor="white",
        )
        ax.add_patch(box)
        ax.text(x + width / 2, y + 0.45, label, ha="center", va="center", fontsize=9)
        centers.append((x + width / 2, y + 0.45, x, width))
    for left, right in zip(centers, centers[1:]):
        ax.add_patch(
            FancyArrowPatch(
                (left[2] + left[3] + 0.03, left[1]),
                (right[2] - 0.03, right[1]),
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.2,
                color=COLORS["neutral"],
            )
        )

    observer = FancyBboxPatch(
        (8.8, 1.35),
        3.2,
        0.9,
        boxstyle="round,pad=0.08,rounding_size=0.08",
        linewidth=1.3,
        edgecolor=COLORS["oracle"],
        facecolor="white",
    )
    ax.add_patch(observer)
    ax.text(
        10.4,
        1.8,
        "Independent effect observer\n+ safety / recovery oracle",
        ha="center",
        va="center",
        fontsize=9,
    )
    ax.add_patch(
        FancyArrowPatch(
            (11.2, 3.47),
            (10.8, 2.3),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.3,
            color=COLORS["oracle"],
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (9.45, 2.28),
            (9.45, 3.47),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.1,
            linestyle="--",
            color=COLORS["oracle"],
        )
    )
    ax.text(9.55, 2.82, "alarm / reconcile", fontsize=8, color=COLORS["oracle"])

    ax.text(1.95, 4.85, "Untrusted computation", ha="center", fontsize=10, weight="bold")
    ax.text(7.0, 4.85, "Deterministic boundary", ha="center", fontsize=10, weight="bold")
    ax.text(11.2, 4.85, "Effects", ha="center", fontsize=10, weight="bold")
    ax.plot([0.25, 3.62], [4.65, 4.65], color=COLORS["untrusted"], linewidth=3)
    ax.plot([3.75, 10.25], [4.65, 4.65], color=COLORS["boundary"], linewidth=3)
    ax.plot([10.35, 12.1], [4.65, 4.65], color=COLORS["environment"], linewidth=3)

    faults = "Fault sites: adaptation · trusted attributes · policy / dependencies · dispatch · receipts · observation"
    ax.text(6.2, 0.62, faults, ha="center", fontsize=9, color=COLORS["unsafe"])
    ax.text(
        6.2,
        0.18,
        "SENTINEL grades the complete proposal-to-effect trace; a policy permit or tool success is not itself a safe outcome.",
        ha="center",
        fontsize=9,
    )
    save(fig, "fig1-assurance-architecture")


def development_results() -> None:
    adaptive = load("iteration-25-adaptive-promptware-v1")
    reports = [
        ("Calendar", load("iteration-21-calendar-promptware-v1")),
        ("Resources", load("iteration-22-resource-transitions-v1")),
        ("Invitation", load("iteration-23-invitation-reconstruction-v1")),
        ("Adaptive", adaptive),
        ("Cut sets", load("iteration-26-boundary-fault-cutsets-v1")),
        ("Challenges", load("iteration-27-prospective-challenges-v1")),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.6), gridspec_kw={"width_ratios": [1, 1.35]})

    defenses = ["none", "schema_allowlist", "fides_correct_label_reconstruction", "sentinel", "always_deny"]
    labels = ["None", "Schema", "IFC*", "SENTINEL", "Always deny"]
    compromised = [adaptive["by_defense"][name]["successful_attack_seeds"] for name in defenses]
    benign = [adaptive["by_defense"][name]["benign_utility"] for name in defenses]
    x = np.arange(len(defenses))
    width = 0.36
    axes[0].bar(x - width / 2, compromised, width, label="Compromised attack seeds / 10", color=COLORS["unsafe"])
    axes[0].bar(x + width / 2, np.array(benign) / 6, width, label="Benign variants retained / 10", color=COLORS["oracle"])
    axes[0].set_xticks(x, labels, rotation=22, ha="right")
    axes[0].set_ylim(0, 11.5)
    axes[0].set_ylabel("Descriptive count (0–10)")
    axes[0].set_title("A. Adaptive development matrix")
    axes[0].legend(frameon=False, fontsize=8, loc="upper right")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].text(0.02, -0.30, "*Conceptual correct-label Fides reconstruction", transform=axes[0].transAxes, fontsize=8)

    names = [name for name, _ in reports]
    agree = np.array([report["receipt_effect_comparisons"].get("agree", 0) for _, report in reports])
    disagree = np.array([report["receipt_effect_comparisons"].get("disagree", 0) for _, report in reports])
    missing = np.array([report["receipt_effect_comparisons"].get("not_computable", 0) for _, report in reports])
    y = np.arange(len(names))
    axes[1].barh(y, agree, label="Agree", color=COLORS["oracle"])
    axes[1].barh(y, disagree, left=agree, label="Disagree", color=COLORS["unsafe"])
    axes[1].barh(y, missing, left=agree + disagree, label="Not computable", color=COLORS["missing"])
    axes[1].set_yticks(y, names)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Trial records")
    axes[1].set_title("B. Receipt vs. safe-effect correspondence")
    axes[1].legend(frameon=False, fontsize=8, ncols=3, loc="lower right")
    axes[1].grid(axis="x", alpha=0.25)
    for i, total in enumerate(agree + disagree + missing):
        axes[1].text(total + max(total * 0.015, 2), i, f"n={total}", va="center", fontsize=8)
    axes[1].text(
        0.0,
        -0.20,
        "Matrices are heterogeneous deterministic inventories; bars must not be pooled into an effectiveness rate.",
        transform=axes[1].transAxes,
        fontsize=8,
    )
    fig.tight_layout()
    save(fig, "fig2-development-results")


def cutsets() -> None:
    report = load("iteration-26-boundary-fault-cutsets-v1")
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 3.8))
    for ax in axes:
        ax.axis("off")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 5)

    axes[0].set_title("A. Prevention failure: minimum cut-set size = 1", pad=10)
    for y, label in [(3.2, "Adapter fault"), (1.5, "Broker fault")]:
        box = FancyBboxPatch((0.8, y), 2.4, 0.8, boxstyle="round,pad=0.06", edgecolor=COLORS["unsafe"], facecolor="white", linewidth=1.4)
        axes[0].add_patch(box)
        axes[0].text(2.0, y + 0.4, label, ha="center", va="center", fontsize=10)
        axes[0].add_patch(FancyArrowPatch((3.25, y + 0.4), (6.0, y + 0.4), arrowstyle="-|>", mutation_scale=14, color=COLORS["unsafe"], linewidth=1.4))
        axes[0].text(7.6, y + 0.4, "Unauthorized effect\n(observer detects)", ha="center", va="center", fontsize=9)

    axes[1].set_title("B. Silent failure: minimum cut-set size = 2", pad=10)
    pairs = [(3.2, "Adapter fault", "Observer fault"), (1.5, "Broker fault", "Observer fault")]
    for y, left, right in pairs:
        for x, label in [(0.35, left), (3.35, right)]:
            box = FancyBboxPatch((x, y), 2.35, 0.8, boxstyle="round,pad=0.06", edgecolor=COLORS["unsafe"], facecolor="white", linewidth=1.4)
            axes[1].add_patch(box)
            axes[1].text(x + 1.175, y + 0.4, label, ha="center", va="center", fontsize=9)
        axes[1].text(3.0, y + 0.4, "+", ha="center", va="center", fontsize=13)
        axes[1].add_patch(FancyArrowPatch((5.75, y + 0.4), (7.25, y + 0.4), arrowstyle="-|>", mutation_scale=14, color=COLORS["unsafe"], linewidth=1.4))
        axes[1].text(8.55, y + 0.4, "Unauthorized effect\nnot reported", ha="center", va="center", fontsize=9)

    assert report["minimal_sentinel_prevention_cut_sets"] == [["sentinel_adapter_fault"], ["sentinel_broker_fault"]]
    assert report["minimal_sentinel_silent_cut_sets"] == [
        ["sentinel_adapter_fault", "sentinel_observer_fault"],
        ["sentinel_broker_fault", "sentinel_observer_fault"],
    ]
    fig.text(0.5, 0.01, "Detection is not prevention: all detected unauthorized effects remain security failures.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig3-minimal-cutsets")


def main() -> None:
    architecture()
    development_results()
    cutsets()


if __name__ == "__main__":
    main()
