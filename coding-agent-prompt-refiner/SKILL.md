---
name: coding-agent-prompt-refiner
description: Transform rough software-change requests into detailed, implementation-ready coding-agent prompts that reduce ambiguity, prevent AI slop, preserve existing architecture, and require evidence-based verification. Use when a user asks to improve, rewrite, structure, or make a coding-agent prompt more precise or likely to produce a high-quality implementation.
---

# Coding Agent Prompt Refiner

## Goal

Turn an informal software request into a **clear, constrained, implementation-ready prompt** for a coding agent.

The output should maximize the chance of:

- correct implementation
- minimal unnecessary code
- readable and maintainable architecture
- preservation of existing behavior
- appropriate reuse of existing components/packages
- deterministic verification
- small, reviewable changes
- fewer security, regression, and UX mistakes

The skill is for **prompt transformation**, not automatic implementation. The finished prompt should be usable directly in Codex, Claude Code, Cursor, or a similar coding agent.

## Core principle

Treat the prompt as a compact engineering contract rather than a prose wish list.

A strong prompt makes the agent understand:

1. **Goal** — what outcome is wanted.
2. **Current state** — what is wrong today, when known.
3. **Desired behavior** — what the user should experience.
4. **Constraints** — what must not change.
5. **Architecture boundaries** — where the agent should and should not modify the system.
6. **Source of truth** — repository code, screenshots, design references, installed package source, or another explicit authority.
7. **Acceptance criteria** — observable, testable requirements.
8. **Verification** — commands and manual checks that prove the work.
9. **Reporting** — what the agent must say it actually changed and verified.

## Required reasoning model

Use this hierarchy of truth when the prompt involves implementation details:

1. Existing code, tests, and runtime behavior.
2. Repository-local docs, ADRs, and conventions.
3. Installed dependency versions, package types, and local source.
4. Current official documentation/changelogs for those exact versions.
5. Official examples.
6. Third-party examples.
7. Model memory.

Never encourage the coding agent to assume an API, package capability, route, variable, feature, or behavior merely because it sounds plausible.

## How to transform a rough request

### Step 1: Extract the actual intent

Rewrite the user's request internally into concrete outcomes.

Separate:

- requested end state
- current problem
- explicit constraints
- implicit constraints that are strongly inferable
- unknowns that must be discovered from the repository

Do not invent missing product requirements.

### Step 2: Identify task type

Classify the request as one or more of:

- bug fix
- UI/UX refinement
- feature
- refactor/simplification
- architecture change
- dependency/library change
- export/import pipeline
- security/privacy
- infrastructure
- performance

Adjust the prompt structure to the task.

Small UI changes do not need an enormous architecture section. Large refactors do.

### Step 3: Establish scope

Explicitly state:

- what is in scope
- what is out of scope
- which existing behavior must remain unchanged

For uncertain implementation details, instruct the agent to inspect the repository rather than asking the user unless the missing information is genuinely product-defining.

### Step 4: Add a research/audit phase when justified

For anything larger than a trivial local change, instruct the agent to inspect before coding.

Typical audit items:

- current implementation
- relevant components
- analogous code
- dependency versions
- data flow/state flow
- persistence
- permissions/auth
- current responsive behavior
- existing design-system primitives
- existing tests
- infrastructure involved

For dependency/package requests, require exact-version verification and current official docs/changelog review.

For design requests, distinguish:

- current application = source of truth for product behavior/content/design system
- provided screenshot/mockup/reference = source of truth for the requested visual direction

Never tell the agent to copy implementation noise from screenshots, such as generated IDs, class names, or DOM structure.

### Step 5: Convert subjective feedback into observable requirements

Translate phrases such as:

- "make it cleaner"
- "better UX"
- "looks basic"
- "simplify it"
- "make it feel premium"
- "make it intuitive"

into concrete constraints such as:

- hierarchy
- density
- spacing
- scanability
- interaction targets
- keyboard behavior
- responsive behavior
- feedback states
- focus states
- consistent design tokens
- reuse of existing primitives
- removal of redundant controls

Do not over-specify purely visual values unless the user or reference gives them.

### Step 6: Separate behavior from implementation

First describe what the user should experience.

Then constrain implementation only where necessary.

Example:

Bad:

> Create a Radix Dialog with fixed width 700px.

Better:

> Present the editor as an inset right-side workspace, not a floating modal. Reuse the existing panel/resizable-layout primitives if available.

Use implementation details when they materially protect the desired outcome, not just because they are convenient.

### Step 7: Add anti-pattern guardrails

Use only guardrails relevant to the task.

Common ones:

- do not rewrite unrelated code
- do not invent backend APIs/data/routes/permissions
- do not duplicate existing primitives
- do not add dependencies without checking whether the existing stack already solves the problem
- do not create renderer-specific hacks when a shared source can be fixed
- do not replace a working architecture solely to reduce file count
- do not hide functionality in UI as a security mechanism
- do not claim verification without actually running it
- do not perform unrelated dependency upgrades

### Step 8: Make acceptance criteria testable

Convert the request into observable statements.

Prefer:

> Selecting PDF starts the browser download automatically and no intermediate download link is rendered.

Over:

> Improve the download experience.

### Step 9: Add verification proportionally

Verification should match task risk.

For UI:

- inspect affected states
- check responsive behavior
- verify keyboard/focus/tooltips where relevant
- run typecheck/lint/tests/build as appropriate

For backend:

- typecheck
- unit/integration tests
- API contract checks
- auth/permission checks
- error paths

For export/rendering:

- generate representative files
- visually compare against the source-of-truth preview
- test formatting edge cases

For refactors:

- verify behavior before/after
- dependency/config audit
- remove dead infrastructure only after reference checks

### Step 10: Require evidence-based reporting

The prompt should tell the coding agent to report:

- changed files/components
- important decisions
- reused components/packages
- actual verification commands/checks
- actual results
- limitations or unresolved issues

Explicitly prohibit claims such as "fully verified", "exact", "production-ready", or "100%" unless the evidence supports them.

## Design/screenshot requests

When screenshots are provided, formulate them as visual references with clear boundaries.

Use language like:

> Use the supplied screenshot as the visual reference for composition, hierarchy, spacing, density, and interaction placement. Do not copy its implementation details or generated markup.

When there are multiple screenshots, identify their roles explicitly, for example:

- current UI/source of truth
- desired visual reference
- secondary interaction reference

Avoid turning an image into an overfitted pixel-copy request unless exact reproduction is explicitly requested.

## Package/library requests

When the user names a package or URL:

- preserve the explicit package preference
- instruct the agent to inspect whether it is already installed
- verify exact installed/version compatibility where relevant
- consult current official documentation when behavior/API matters
- prefer a small, maintained dependency over custom code when it genuinely reduces complexity
- do not replace simple existing code with a dependency merely because the package exists

## Refactor/simplification requests

Interpret "less code" as:

> fewer unnecessary moving parts while preserving readability, reliability, and behavior

not:

> fewer lines at any cost.

The prompt should tell the agent to inspect before deleting code and to compare service boundaries, abstractions, dependencies, duplicated logic, and configuration.

## Security/privacy/legal-sensitive requests

For these tasks:

- distinguish technically verifiable requirements from organizational/legal requirements
- do not claim absolute compliance
- require explicit verification of actual code/configuration
- identify items that require external/legal/organizational review as such
- never suggest that hiding a UI element is a security boundary

## Output style

Return **one finished prompt** by default.

Use a short preamble outside the writing block explaining the main improvement, then provide the complete prompt in a `writing` block using:

- `variant="document"`
- a descriptive `title`
- a unique 5-digit id

The prompt itself should be directly copy-pasteable into a coding agent.

Do not surround the finished prompt with extra commentary inside the writing block.

## Prompt structure

Use this structure when appropriate:

```md
Please [goal].

## Goal
...

## 1. Audit before implementation
...

## 2. Current problem / relevant context
...

## 3. Required behavior
...

## 4. UI / UX requirements
...

## 5. Architecture and implementation constraints
...

## 6. Preserve existing behavior
...

## 7. Responsive / accessibility / security considerations
...

## 8. Acceptance criteria
...

## 9. Verification
...

## 10. Final report
...
```

Do not force every section into every task. Remove sections that add no value.

## Quality gate before responding

Before producing the final prompt, check:

- Is the desired outcome unambiguous?
- Did I preserve the user's actual intent?
- Did I avoid inventing product requirements?
- Did I define what should remain unchanged?
- Did I tell the coding agent what to inspect before coding where necessary?
- Did I make subjective requests observable?
- Did I avoid implementation over-prescription?
- Did I include only relevant anti-pattern guardrails?
- Are acceptance criteria testable?
- Is verification proportional to the task?
- Does the prompt require honest reporting of actual verification?
- Is the prompt small enough to remain usable while still being detailed?

## Important behavior

Do not merely polish the user's grammar.

The purpose of this skill is to **add engineering precision** while preserving the user's desired feature or change.

Do not turn every request into a giant enterprise specification. Add detail where it reduces implementation ambiguity or regression risk.

When the request contains a likely hidden failure mode, encode that failure mode as a guardrail.

Examples:

- "make PDF match Word" → require root-cause analysis, shared source of truth, and actual file comparison
- "use a package instead of custom code" → inspect current dependencies and compare package complexity/maintenance before adding one
- "make sidebar more intuitive" → define information hierarchy, scanning, interaction targets, focus/hover states, and preserve semantics
- "remove Gotenberg" → audit the whole conversion pipeline and remove obsolete infrastructure only after usage verification
- "add autocomplete for template strings" → derive suggestions from the actual supported variable schema rather than inventing tokens

The finished prompt should make a strong coding agent **inspect, reason, implement narrowly, verify concretely, and report honestly**.
