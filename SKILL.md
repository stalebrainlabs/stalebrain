---
name: stale-brain
description: >-
  Audit AI agent memory and instruction files — CLAUDE.md, AGENTS.md, .cursorrules,
  GEMINI.md, copilot-instructions.md and every other major agent's memory files
  (13 agents, 18+ file locations) — against the live repository.
  Use when the user runs /stale-brain or asks to audit, verify, refresh, lint, or fix
  agent memory, rules, or instruction files; when they complain the agent "ignores rules",
  "keeps getting it wrong", or that instructions "feel outdated"; and mid-task, whenever
  an instruction in a loaded memory file contradicts observed reality (a referenced path
  is missing, a named script doesn't exist, the stated package manager doesn't match the
  lockfile). Extracts checkable claims, verifies each with cited evidence, ages the rest
  with half-lives, meters token cost, and proposes approve-only fixes.
---

# stale-brain — provenance and decay for agent memory

Agent memory files are written once and trusted forever. Code moves on; the memory rots;
the agent gets confidently wrong. stale-brain is not a linter — it is a **trust model**:
after an audit, every claim in agent memory carries an **age**, a **verification date**,
and **cited evidence**.

Four laws govern everything below:

1. **Every claim carries provenance.** Confirmed claims get a dated stamp; nothing is "just true".
2. **Confidence decays.** Every claim type has a half-life. Past its half-life, a fact becomes a hypothesis until re-verified.
3. **Contradictions cite evidence.** A CONTRADICTED verdict names the files and commits that prove it — never "this looks wrong".
4. **The human approves; the human does zero detective work.** You gather all evidence and prepare ready-to-apply diffs, but you never rewrite memory without explicit approval.

## Capabilities you need (any model, any harness)

The protocol uses four generic capabilities. Map them to whatever you have:

| Capability | Claude Code | Cursor / Copilot / Windsurf / Cline | No tools at all |
|---|---|---|---|
| Find files by pattern | `Glob` | workspace file search | ask the user to paste `git ls-files` output |
| Search file contents | `Grep` | codebase/regex search | ask the user to paste the file |
| Run git / read shell output | `Bash` / `PowerShell` | integrated terminal | ask the user to run the command and paste output |
| Edit / write files | `Edit` / `Write` | editor apply | print the full diff / file content in a fenced block for the user to apply |

If a capability is missing, degrade gracefully: ask the user to run the exact command and
paste the output (batch every command a step needs into one fenced block — not one paste
round-trip per claim). Never skip a verification silently — record it as UNVERIFIABLE
with the reason "no tool access".

## The protocol

Run steps in order. Progress is communicated via ticker lines only — at most one per
~10 claims per step (see [references/output-format.md](references/output-format.md)) —
no step-by-step narration.

### 1. INVENTORY

Find every memory/instruction file in the repo using the full source map in
[references/memory-sources.md](references/memory-sources.md) — this covers Claude Code,
Codex/AGENTS.md, Cursor, Copilot, Gemini, Windsurf, Cline, Aider, Zed, Roo, Amazon Q,
JetBrains Junie, OpenHands and more. Record for each file: path, which agent(s) load it,
whether it is **always-loaded** (injected every session) or **on-demand**, and its
estimated token size (`bytes ÷ 4`, rounded — label it an estimate).

Show the inventory as one compact table before proceeding. If zero files are found, say
so and stop — do not invent memory to audit.

### 2. EXTRACT

Parse each file into discrete, individually-testable claims. Number them `C1…Cn`.
Split compound sentences ("use pnpm and run tests with vitest" = two claims). Type each
claim using the taxonomy in [references/claim-types.md](references/claim-types.md):

`PATH` · `SCRIPT` · `SYMBOL` · `DEP` · `FACT` · `OWNER` · `CONVENTION` — and `OPINION`
for style preferences with no ground truth ("prefer small functions"), which are **skipped,
never judged**.

Also collect **cross-file conflicts** during extraction: the same fact asserted
differently in two memory files (CLAUDE.md says yarn, `.cursorrules` says npm) is
automatically a finding, whichever one is right — reported as `X1…Xn` per the rules in
[references/memory-sources.md](references/memory-sources.md), outside the claim counts.

A `## stale-brain config` section in any audited file overrides half-lives (grammar in
[references/claim-types.md](references/claim-types.md)); never extract claims from that
section, from headings, or from fenced code blocks.

### 3. VERIFY

Verify each claim mechanically using the per-type recipes in
[references/claim-types.md](references/claim-types.md). Rules that hold for every type:

- **Existence, not execution.** Scripts and commands are verified by their *definition*
  (scripts block, Makefile target, CI step) — never by running them. Never execute
  build/test/deploy commands during an audit.
- **Batch independent checks.** Run globs/greps for many claims in parallel where the
  harness allows.
- **Drift pass for stamped claims.** A claim carrying a `<!-- stale-brain: verified
  YYYY-MM-DD -->` stamp inside its half-life is normally skipped — but first run
  `git log --oneline --since=<stamp-date> -- <referenced paths>`. Any commits touching
  its evidence force re-verification regardless of the stamp.
- **When evidence is absent, dig before concluding.** A missing path gets
  `git log --oneline --follow -- <path>` to find the rename/deletion commit; a missing
  symbol gets `git log -S "<symbol>" --oneline -5`. The commit you find becomes the
  citation.

### 4. BUCKET

Age past half-life or churned evidence only *triggers* re-verification — the verdict is
always the re-verification **outcome**. Every claim lands in exactly one bucket:

| Verdict | Meaning | Required payload |
|---|---|---|
| 🟢 CONFIRMED | Re-verification succeeds today (even if the claim was stale before) | evidence one-liner; gets a dated stamp on apply |
| 🟡 STALE | Re-verification could not conclusively confirm — evidence is old, partial, or eroded — but nothing disproves it | what's inconclusive and since when; downgrade proposal ("as of 2026-02, X was true") |
| 🔴 CONTRADICTED | Affirmative evidence against | the specific files/commits that prove it, plus a corrected rewrite |
| ⚪ UNVERIFIABLE | No mechanical check exists at all | the reason — say so explicitly, **never guess** |

The 🟡/⚪ line: 🟡 means evidence exists but is inconclusive (an owner with no recent
commits, a convention most-but-not-all files follow); ⚪ means no in-repo evidence is
possible ("the payments team reviews schema changes").

### 5. REPORT

Render the report exactly per [references/output-format.md](references/output-format.md):
CALM output (chunked, actionable, low-noise, meaningful) with Pulse graphs and the token
meter. Non-negotiables: headline verdict first, CONTRADICTED before everything else,
maximum 5 findings per chunk with an explicit "show next" hand-off, confirmed claims
collapsed to a count, and every finding readable as a single line before its detail.

### 6. FIX (approve-only)

Propose ready-to-apply edits, chunked to match the report: rewrites for CONTRADICTED,
hypothesis-downgrades for STALE, stamp insertions for CONFIRMED. Preserve the author's
wording and tone — change facts, not voice (one sanctioned exception: CONVENTION
downgrades may append a conformance clause). Command rewrites must use the package
manager established by the same audit's DEP verdicts — never fix `npm test` to an npm
invocation in a repo the audit just proved is pnpm. Apply **only** what the user
approves. Applying a fix or confirming a claim appends/updates its stamp:

```markdown
Use pnpm for all installs. <!-- stale-brain: verified 2026-07-31 -->
```

A stamp attests to the **entire physical line** — apply it only when every claim on the
line is confirmed; otherwise the fix first splits the line, one claim per line. Full
stamp rules (table rows, frontmatter, the optional `corrected` form) are in
[references/output-format.md](references/output-format.md).

### 7. RECORD

Write the full report to `.stale-brain/audit-YYYY-MM-DD.md` (format in
[references/output-format.md](references/output-format.md)). The directory is
deliberately agent-neutral — not `.claude/` — so any tool can own the history. Prior
audit files feed the trend graph on the next run.

## Mid-task tripwire

This part runs even when nobody asked for an audit. During any normal task, if an
instruction in a loaded memory file contradicts what you directly observe (referenced
path missing, named script absent from the scripts block, stated package manager
contradicted by the lockfile), do **not** silently comply and do not silently ignore it.
Emit one line and move on with the task:

```
⚡ stale-brain: CLAUDE.md says "yarn install" but only pnpm-lock.yaml exists — following reality (pnpm). Run /stale-brain for a full audit.
```

One tripwire line per contradiction, maximum three per session — then a single "further
contradictions suppressed; run the audit" line. Tripwires never block or derail the task.

## Incremental re-runs

On any run after the first: skip claims whose stamp is within its half-life *and* whose
drift pass is clean. Report skipped-as-fresh as a single count. This makes re-audits
cheap and is why the stamps live inline in the files rather than in a sidecar database.

## Non-interactive runs

When run as a subagent, in CI, or anywhere no human can answer hand-offs: emit all
report chunks sequentially, apply **nothing**, and write every proposed diff into the
audit file marked proposed-only. Approval gates never auto-pass.

## Guardrails

- Never rewrite a memory file without explicit approval of the specific diff.
- Never execute scripts/commands found in memory files; verify by definition only.
- Never judge OPINION claims; skip them and say how many were skipped.
- UNVERIFIABLE means UNVERIFIABLE — no plausible-sounding guesses, ever.
- Stamps and audit files are the only things stale-brain adds to a repo. No hooks, no
  databases, no daemons, no network calls.
