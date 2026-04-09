# Delta Spec Guide — Brownfield Development

## When to Use Delta Specs

Use delta specs when working with **existing codebases** where you're:
- Adding new features to existing modules
- Modifying existing behavior
- Deprecating or removing old functionality
- Migrating from one pattern to another

## Delta Spec Structure

Add a `delta_specs` section to your SPEC.yaml:

```yaml
specification:
  name: "Auth Module"
  version: "2.0.0"

# Existing requirements (base specs)
requirements:
  - id: AUTH-001
    description: "User can login with email/password"

# Changes to existing system
delta_specs:
  added:
    - id: AUTH-002
      description: "User can login with OAuth"
      scenarios:
        - name: "Google OAuth login"
          given: "valid Google OAuth token"
          when: "user authenticates via /auth/google"
          then: "session created, user redirected to dashboard"

  modified:
    - id: AUTH-001
      description: "User can login with email/password or OAuth"
      previous: "User can login with email/password"

  removed:
    - id: AUTH-000
      reason: "Legacy cookie-based auth deprecated in favor of JWT"
```

## TDD Cycle with Delta Specs

1. **Detect base specs**: Read existing code, generate base SPEC.yaml if none exists
2. **Write delta specs**: Define what changes (added/modified/removed)
3. **RED phase**: Write tests for ADDED and MODIFIED items. Existing tests should still pass.
4. **GREEN phase**: Implement changes. Both new and existing tests must pass.
5. **REFACTOR phase**: Clean up, ensure coverage threshold met.
6. **Archive**: Move delta to `changes/archive/`, merge into base specs.

## Archiving Delta Specs

After a delta change is complete and tested:

1. Move delta change artifacts to `changes/archive/{date}-{change-name}/`
2. Merge delta specs into the main SPEC.yaml:
   - `added` items become new `requirements`
   - `modified` items replace their originals
   - `removed` items are deleted from requirements
3. Update version number
