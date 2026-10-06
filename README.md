<div align="center">

# Coding Agent Prompt Refiner

**Turn a rough software-change request into a clear, scoped prompt a coding agent can act on directly.**

Works with Codex, Claude Code, Cursor, or similar agents.

[What it does](#what-it-does) · [Example](#example) · [Files](#files) · [Install](#install) · [Auto-install prompt](#auto-install-prompt)

</div>

> [!NOTE]
> It rewrites prompts. It does not implement the change.

## What it does

The skill treats a prompt as a short engineering contract. Given an informal request, it:

1. **Extracts the intent.** The end state, the current problem, the explicit constraints, and the unknowns the agent must discover in the repo. It does not invent product requirements.
2. **Classifies the task** (bug fix, UI/UX, feature, refactor, dependency change, security, performance, and so on) and sizes the prompt to match.
3. **Sets scope.** What is in scope, what is out of scope, and what existing behavior must not change.
4. **Adds an audit step** before coding when the task is more than a trivial local change.
5. **Turns subjective feedback into observable requirements.** "Make it cleaner" or "better UX" becomes hierarchy, spacing, focus states, and reuse of existing primitives.
6. **Describes the behavior first** and constrains the implementation only where that protects the outcome.
7. **Adds only the guardrails that fit the task**, such as "do not invent APIs", "do not add dependencies without checking the existing stack", or "do not rewrite unrelated code".
8. **Writes acceptance criteria** that a person or a deterministic check can confirm.
9. **Sizes verification** to the risk of the change.
10. **Requires an honest report.** The agent states what it changed and what it actually verified, without unsupported claims like "fully verified" or "production-ready".

It also names a source of truth for each part of the task:

| Part of the task | Source of truth |
|------------------|-----------------|
| Architecture and behavior | The repo |
| Visual direction | Screenshots |
| API behavior | Installed package source and official docs |
| Correctness | Tests or compilers |

## When to use it

Use it when you want to improve, rewrite, structure, or tighten a prompt before handing it to a coding agent.

## Output

One finished, copy-pasteable prompt. It follows the sections in [`output-template.md`](coding-agent-prompt-refiner/references/output-template.md) and drops any section that adds nothing for the task:

`Goal` → `Audit` → `Current problem` → `Required behavior` → `UI/UX` → `Architecture constraints` → `Preserve existing behavior` → `Acceptance criteria` → `Verification` → `Final report`

## Example

**Input**

> make the sidebar more intuitive

**The refined prompt**

- Tells the agent to audit the current sidebar and its design-system primitives first.
- Defines "intuitive" as information hierarchy, scannability, interaction target size, and hover and focus states.
- Keeps the existing navigation behavior unchanged.
- Lists testable acceptance criteria.
- Asks for a report of the checks that were actually run.

## Files

| File | Purpose |
|------|---------|
| [`coding-agent-prompt-refiner/SKILL.md`](coding-agent-prompt-refiner/SKILL.md) | The skill: transformation steps, guidance per request type, and a quality gate |
| [`coding-agent-prompt-refiner/references/heuristics.md`](coding-agent-prompt-refiner/references/heuristics.md) | Rules for intent, scope, source of truth, acceptance criteria, verification, and dependencies |
| [`coding-agent-prompt-refiner/references/output-template.md`](coding-agent-prompt-refiner/references/output-template.md) | Section template for the finished prompt |

## Install

Copy the `coding-agent-prompt-refiner/` folder into one of these:

| Scope | Location |
|-------|----------|
| All projects | `~/.claude/skills/` |
| One project | The project's `.claude/skills/` |

## Auto-install prompt

> [!TIP]
> Paste this into Claude Code or Codex. It installs the skill for both tools and adds a rule to your global `CLAUDE.md` and `AGENTS.md` so the agent refines every code-change request before working on it.

````text
Install the coding-agent-prompt-refiner skill and make it the first step for code-change requests.

1. Install the skill
   - Clone https://github.com/Niggo2k/skills into a temporary folder.
   - Copy its `coding-agent-prompt-refiner/` folder to `~/.agents/skills/coding-agent-prompt-refiner/` (Codex).
   - Make it available to Claude Code at `~/.claude/skills/coding-agent-prompt-refiner/`. Use a symlink to the `~/.agents/skills` copy if that is how other skills are set up there, otherwise copy the folder.
   - If either target already exists, show me the differences and ask before overwriting.
   - Delete the temporary clone.

2. Add the rule to my global instruction files
   - Files: `~/.claude/CLAUDE.md` (Claude Code) and `~/.codex/AGENTS.md` (Codex). Create a file if it does not exist.
   - If a "## Prompt Refinement" section already exists in a file, leave that file unchanged.
   - Otherwise append this section exactly, without changing anything else in the file:

   ```md
   ## Prompt Refinement

   Before working on any request to change code (feature, fix, redesign, refactor, UI change), run the `coding-agent-prompt-refiner` skill on my original prompt. Show me the refined prompt, then carry out the refined prompt instead of the original.

   Example: "Please redesign this element" becomes a prompt with a goal, what to audit first, concrete UI requirements, what must stay unchanged, acceptance criteria, and verification steps. You then implement that prompt.

   Skip this for questions, one-line mechanical edits, and git or PR commands.
   ```

3. Verify and report
   - Confirm `SKILL.md` exists at both skill paths.
   - Confirm each instruction file contains exactly one "## Prompt Refinement" section.
   - List every file you created, changed, or skipped. Tell me the rule takes effect in new sessions.
````
