# SPEC.yaml Format Reference

## Standard Format (Greenfield)

```yaml
specification:
  name: "Feature Name"
  version: "1.0.0"
  description: "What this feature does"

tdd_config:
  test_framework: pytest    # pytest | jest | go test | cargo test
  coverage_threshold: 80    # Minimum %, hard requirement
  test_types: [unit, integration, acceptance]

requirements:
  - id: FEAT-001            # Unique ID, prefix by domain
    description: "..."
    priority: high           # high | medium | low
    scenarios:
      - name: "scenario name"
        given: "precondition"
        when: "action performed"
        then: "expected outcome"
```

## Delta Format (Brownfield)

For modifying existing code, add a `delta_specs` section:

```yaml
delta_specs:
  added:
    - id: FEAT-NEW-001
      description: "New capability"
      scenarios: [...]

  modified:
    - id: FEAT-001
      description: "Updated behavior"
      previous: "What it used to do"
      scenarios: [...]       # New behavior scenarios

  removed:
    - id: LEGACY-001
      reason: "Replaced by FEAT-NEW-001"
```

## Requirement ID Conventions

| Prefix | Domain |
|--------|--------|
| FEAT- | Feature requirements |
| AUTH- | Authentication/authorization |
| API- | API endpoints |
| DATA- | Data models/persistence |
| UI- | User interface |
| PERF- | Performance requirements |

## Scenario Best Practices

- One scenario per behavior (not per test)
- Given: describe the state, not the setup steps
- When: single action, not a sequence
- Then: observable outcome, not implementation detail

**Good:**
```yaml
- name: "rate limit exceeded"
  given: "user has made 100 requests in the last minute"
  when: "user makes another request"
  then: "returns 429 Too Many Requests"
```

**Bad:**
```yaml
- name: "test rate limiter"
  given: "create Redis connection and set counter to 100"
  when: "call rate_limit() and then call api()"
  then: "function returns false and Redis key has TTL"
```
