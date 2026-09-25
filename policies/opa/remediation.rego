package sentinel

default allow := false

allow if {
    input.proposal.capability_name == "set_replicas"
    service := input.proposal.arguments.service
    service in input.trusted.allowed_services
    service in input.trusted.allowed_scope
    replicas := input.proposal.arguments.replicas
    is_number(replicas)
    replicas >= 0
    replicas <= 3
}
