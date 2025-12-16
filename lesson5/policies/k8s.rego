package cnpe.compliance

default allow := false

# Collect violations as a set of strings (Rego v1 syntax)
violations contains msg if {
  input.kind == "Deployment"
  not input.metadata.labels.team
  msg := "missing label: metadata.labels.team"
}

violations contains msg if {
  input.kind == "Deployment"
  not input.metadata.labels.environment
  msg := "missing label: metadata.labels.environment"
}

violations contains msg if {
  input.kind == "Deployment"
  c := input.spec.template.spec.containers[_]
  endswith(c.image, ":latest")
  msg := sprintf("image tag must not be latest: %s", [c.image])
}

violations contains msg if {
  input.kind == "Deployment"
  c := input.spec.template.spec.containers[_]
  not c.resources.requests.cpu
  msg := sprintf("missing cpu request for container: %s", [c.name])
}

violations contains msg if {
  input.kind == "Deployment"
  c := input.spec.template.spec.containers[_]
  not c.resources.requests.memory
  msg := sprintf("missing memory request for container: %s", [c.name])
}

violations contains msg if {
  input.kind == "Deployment"
  c := input.spec.template.spec.containers[_]
  not c.resources.limits.cpu
  msg := sprintf("missing cpu limit for container: %s", [c.name])
}

violations contains msg if {
  input.kind == "Deployment"
  c := input.spec.template.spec.containers[_]
  not c.resources.limits.memory
  msg := sprintf("missing memory limit for container: %s", [c.name])
}

violations contains msg if {
  input.kind == "Deployment"
  not input.spec.template.spec.securityContext
  msg := "missing pod securityContext (runAsNonRoot required)"
}

violations contains msg if {
  input.kind == "Deployment"
  sc := input.spec.template.spec.securityContext
  sc.runAsNonRoot != true
  msg := "pod must set securityContext.runAsNonRoot=true"
}

allow if {
  count(violations) == 0
}

