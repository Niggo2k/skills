# Prompt Refinement Heuristics

## Preserve intent

Do not alter the requested product outcome. Clarify it; do not redesign the request itself.

## Scope control

Every non-trivial prompt should make unrelated changes explicitly out of scope when that is useful.

## Source-of-truth mapping

Name the authoritative source for each part of the task:

- repository = architecture and existing behavior
- current rendered UI = existing product behavior
- screenshot/reference = requested visual direction
- installed package types/source = API truth
- official docs/changelog = version-specific external API truth
- generated output = export/rendering truth
- compiler/tests/scanners = deterministic correctness evidence

## Good acceptance criteria

Criteria should be observable by a human or deterministic check.

Avoid vague words without operational meaning: better, modern, clean, polished, robust, optimized.

When such words are important, translate them into concrete properties.

## Good verification

Verification should test the failure mode described by the request.

A successful build does not prove visual parity.
A passing typecheck does not prove authorization correctness.
A generated file does not prove export fidelity.
A removed environment variable from `.env.example` does not prove it is unused.

## Dependency discipline

The existence of a package is not proof that adding it is better than a few readable lines.

Prefer fewer moving parts, not fewer lines at any cost.

## Refactor discipline

Refactoring should preserve contracts unless the prompt explicitly changes them.

Avoid opportunistic cleanup that obscures the intended diff.
