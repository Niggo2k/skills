---
name: auto-commit
description: Commit the currently staged git changes as a series of focused commits, one per logical change (feature, fix, refactor, docs, config), splitting files at hunk level when needed and never committing unstaged or untracked work. Use this whenever the user asks to commit their staged changes, "commit what I staged", "commit by functionality / by feature / by implementation", "split the staged changes into commits", "make atomic commits", or "commit these changes properly", even if they don't say "split". Not for writing a single commit message, amending, pushing, or opening PRs.
---

# Auto Commit

Turn the git index into a clean series of commits, each covering one purpose, and leave the working tree exactly as it was.

The user staged a specific set of changes on purpose. Anything not staged is work in progress that must stay out of every commit. That is why this skill never runs `git add`: on a partially staged file it would pull in the unstaged edits too. All staging goes through `git apply --cached` with patches cut from the original staged diff.

`scripts/hunks.py` (next to this file) lists the hunks of a patch and rebuilds a patch from a chosen subset. Call it with the absolute path of this skill directory.

## 1. Preflight

Stop and tell the user, without committing anything, if any of these are true:

- `git diff --cached --quiet` exits 0 (nothing staged).
- A merge, rebase, cherry-pick, or revert is in progress (`.git/MERGE_HEAD`, `rebase-merge/`, `rebase-apply/`, `CHERRY_PICK_HEAD`, `REVERT_HEAD` under `git rev-parse --git-dir`).
- `git symbolic-ref -q HEAD` fails (detached HEAD) or `git rev-parse -q --verify HEAD` fails (no commits yet).

## 2. Snapshot

```bash
SNAP=$(mktemp -d)
BASE=$(git rev-parse HEAD)
git diff --cached --binary > "$SNAP/staged.patch"
git diff --binary > "$SNAP/unstaged.patch"
```

`staged.patch` is the restore point and the source for every group patch. `unstaged.patch` is used to prove the working tree was not touched.

## 3. Understand and group

Read `git diff --cached --stat`, the full staged diff, and `python3 <skill-dir>/scripts/hunks.py list "$SNAP/staged.patch"`. Each line of the list is one hunk ID (`H1`, `H2`, ...). New, deleted, renamed, binary, and mode-changed files appear as one unsplittable ID.

Group the hunk IDs by purpose: what the change does for the codebase, not which folder or file type it touches. Good groups:

- a feature with its implementation, wiring, and tests
- a bug fix with its regression test
- a pure refactor or rename that changes no behavior
- docs, config, dependency, or formatting changes that stand on their own

Rules of thumb:

- One coherent change stays one commit. Don't split for the sake of it. A single group is a valid result.
- Split a file across groups only when its hunks clearly serve different purposes.
- Every hunk ID goes into exactly one group.
- A hunk that serves two groups (for example, one test hunk covering a fix and a new feature) goes into the later group, so no commit references code that doesn't exist yet. Mention it in the report.
- Order groups so each commit builds on the earlier ones: shared types, schema, or helpers first, then the code using them, then docs.

## 4. Write messages

Run `git log -n 20 --format=%s` and mirror the repo's style (Conventional Commits, prefixes, capitalization, tense). If there is no clear pattern, use Conventional Commits: `type(scope): subject` with types `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`.

- Subject in imperative mood, 72 characters max, no trailing period.
- Add a body only when the reason for the change isn't obvious from the diff.
- Don't add `Co-Authored-By`, "Generated with", or other attribution trailers.

## 5. Commit

Unstage everything (this keeps the working tree), then build each commit from its hunks:

```bash
git reset -q
python3 <skill-dir>/scripts/hunks.py pick "$SNAP/staged.patch" H1 H3 > "$SNAP/g1.patch"
git apply --cached "$SNAP/g1.patch"
git commit -q -F - <<'EOF'
feat(auth): add token refresh
EOF
```

Repeat for each group in order. Commit without asking for confirmation: the user asked for the commits, and they can undo them with `git reset HEAD~N`.

Don't pass `--no-verify`. If a hook fails, or a hook changes files so that `git status` shows changes you didn't expect, go to step 7.

## 6. Verify

Both checks must print nothing:

```bash
git diff --binary "$BASE" HEAD | diff - "$SNAP/staged.patch"
git diff --binary | diff - "$SNAP/unstaged.patch"
```

The first proves the commits contain exactly what was staged. The second proves the unstaged work is untouched. `git diff --cached` should also be empty.

## 7. Recover on failure

If any step after the snapshot fails (patch doesn't apply, hook rejects, a verify check differs), put the user back where they started:

```bash
git reset -q "$BASE"
git apply --cached "$SNAP/staged.patch"
```

`git reset` without `--hard` moves HEAD and the index only. The working tree is never touched. Don't use `git stash`, `git reset --hard`, `git checkout -- <path>`, or `git restore` on the working tree. Then report what failed and the exact error.

## 8. Report

Keep it short:

- one line per commit: short SHA, subject, files
- what is still unstaged or untracked (from `git status --short`), so the user sees nothing was swept in
- the undo command: `git reset HEAD~N`

Don't push, open a PR, or create a branch unless asked.
