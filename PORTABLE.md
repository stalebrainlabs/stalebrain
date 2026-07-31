# stale-brain (portable): paste this into any AI agent

You are running **stale-brain**: an audit of this repository's AI memory/instruction
files against the live code. Not a linter but a trust model: after this audit, every claim
in agent memory carries an age, a verification date, and cited evidence. Follow this file
exactly. It is self-contained and works with any agent.

**Degraded modes.** Missing a read tool (file listing, content search, shell): ask the
user to run the exact commands and paste the output; batch every command a step needs
into ONE fenced block, never one paste round-trip per claim; inventory without tools =
ask for `git ls-files` plus a paste of each memory file (estimate tokens from pasted
length). Missing file-write access: print the complete audit file and every approved
diff in fenced blocks for the user to save/apply. Never skip a check silently; record
it ⚪ with reason "no tool access". Non-interactive runs (CI, subagent): emit all report
chunks sequentially, apply nothing, record diffs as proposed-only.

## 1 · Inventory

Find every file below that exists (root and subdirectories). For each: path, which agent
loads it, always-loaded or on-demand, estimated tokens (file bytes ÷ 4, label "est.").

`CLAUDE.md` · `CLAUDE.local.md` · `.claude/**/*.md` · `AGENTS.md` · `.cursorrules` ·
`.cursor/rules/**/*.mdc` · `.github/copilot-instructions.md` ·
`.github/instructions/*.instructions.md` · `GEMINI.md` · `.windsurfrules` ·
`.windsurf/rules/**` · `.clinerules` (file or dir) · `.roo/rules/**` · `.rules` (Zed) ·
`.amazonq/rules/**` · `.junie/guidelines.md` · `.openhands/microagents/*.md` ·
`CONVENTIONS.md` (only if `.aider.conf.yml` references it) · anything the user adds.

Scoped rules (frontmatter `globs`/`alwaysApply: false`, `*.instructions.md`) are
on-demand; when loading is ambiguous, classify always-loaded (conservative for a cost
meter) and mark `†`. Out of scope: README/CONTRIBUTING/docs (human docs), lockfiles/
manifests/CI (those are *evidence*), transcripts. Show the inventory as one table.
Zero files → say so and stop.

## 2 · Extract

Split each file into numbered, individually-testable claims `C1…Cn` (compound sentences
= multiple claims; keep file:line and a faithful short quote). Type each:

| Type | Claims that… | Half-life |
|---|---|---|
| PATH | a file/dir exists | 30d |
| SCRIPT | a named command/script exists | 30d |
| SYMBOL | a function/class exists | 45d |
| DEP | a dependency/version/package manager | 60d |
| FACT | other checkable assertions | 90d |
| OWNER | a person/team owns an area | 90d |
| CONVENTION | the code follows a pattern | 120d |
| OPINION | style preference, no ground truth | skip, never judge |

A `## stale-brain config` section in any audited file overrides half-lives: one
directive per line, `half-life PATH: 14d` (days only, TYPE uppercase); malformed lines
reported and ignored; if two files set the same type, the strictest wins. Never extract
claims from a config section, headings, or fenced code blocks.

**Cross-file conflicts:** the same fact asserted differently in two files (CLAUDE.md:
yarn, .cursorrules: npm) is a conflict finding `X1…Xn`, anchored to both sides
(`CLAUDE.md:12 ↔ .cursorrules:3`), excluded from claim counts and the health score.
When verification already flags a side, fold the conflict into that finding's evidence;
render a standalone X-finding only when neither side is flagged (its action: "ask the
user which is true").

## 3 · Verify (existence, not execution; never run scripts you find)

Aging or churn only *triggers* re-verification; the verdict is always the outcome.
Quoting note: pickaxe (`-S`) patterns containing double quotes must be single-quoted to
survive both Git Bash and PowerShell.

- **PATH**: does it exist? Missing → `git log --oneline -- <path>` for the vanishing
  commit, then `git log --oneline --name-status -1 <commit>` (no pathspec): `R100 old
  new` = renamed (new path goes in the rewrite), `D old` = deleted → 🔴 citing the
  commit. No git history at all → ⚪.
- **SCRIPT**: is it defined (package.json scripts / Makefile / justfile / Taskfile / CI
  steps)? Absent or different name → 🔴, cite the definition that exists and when it
  changed (`git log -S '"test":' --oneline -5 -- package.json`). Rewrites must use the
  package manager this audit's DEP verdicts established.
- **SYMBOL**: search for the definition; absent → `git log -S "<symbol>" --oneline -5`
  for the removal commit, then `git log -p -S "<symbol>" -1` to read the added-line
  counterpart as the replacement name → 🔴 with commit + rewrite.
- **DEP**: package manager = whichever lockfile exists (`pnpm-lock.yaml` / `yarn.lock` /
  `package-lock.json` / `bun.lockb`); multiple lockfiles = a finding in itself, and the
  `packageManager` field in package.json wins. Versions = the manifest's constraint
  (lockfile resolution only if the claim is about the exact installed version).
- **FACT**: reduce to an observable proxy (vercel.json, turbo.json…); no proxy → ⚪.
- **OWNER**: named in CODEOWNERS → 🟢; CODEOWNERS names someone else → 🔴. No
  CODEOWNERS: map the handle to a git identity (`git log --author=<handle>` matches
  name/email); maps and active in `git shortlog -sn HEAD --since="9 months ago" --
  <area>` → 🟢; maps but inactive → 🟡; cannot map at all → ⚪.
- **CONVENTION**: sample 3–5 governed files; all conform → 🟢 (note sample size),
  majority → 🟡, minority → 🔴, with counter-examples cited.
- **Stamped claims** (`<!-- stale-brain: verified YYYY-MM-DD -->` within half-life):
  skip as fresh, unless `git log --oneline --since=<stamp> -- <its paths>` is non-empty
  → re-verify. (Shallow clone → don't trust an empty drift pass; re-verify.)
- Conditional claims ("if you touch billing, ask @maria"): verify the factual parts,
  leave the conditional logic alone.

## 4 · Verdicts

🟢 CONFIRMED: re-verification succeeds today (even if it was stale before); stamped on
apply. 🟡 STALE: check came back inconclusive (owner inactive, convention
majority-not-all, evidence churned without resolution); downgrade to "as of <date>, X
was true". 🔴 CONTRADICTED: affirmative evidence against; cite the exact files/commits
plus a corrected rewrite. ⚪ UNVERIFIABLE: no mechanical check exists; state the
reason; never guess. Unstamped claims count as *at* half-life (eligible for
verification, not auto-stale).

## 5 · Report (CALM rules: hard rules)

The initial report is one screen: each verdict section caps at 5 findings, overflow
elided `[first 5 of N]` with a hand-off (`→ 8 more, say "next"`). Verdict first,
evidence second, action third; every finding ends in an action. No preamble, no
narration; progress is ticker lines only, at most one per ~10 claims, counts in
severity order (`[stale-brain] verifying 20/39 · 🔴6 🟡4 ⚪2 🟢8`). Confirmed = a count
(the list, if asked for, chunks at ≤10). Omit empty sections. Report order: headline
health bar → 🔴 (X-conflicts at its end) → 🟡 → ⚪ → 🟢 count → token meter → trend
(re-audits only; omit on first audit) → next-actions line.

```
🔴🔴🔴🟡🟡🟢🟢🟢🟢🟢  health 58/100 · 47 claims from 7 files (8 fresh-skipped, 3 opinions skipped)
health = (confirmed + 0.5·stale) / (confirmed + stale + contradicted) × 100
  note: confirmed INCLUDES fresh-skipped (a valid stamp is a confirmation); ⚪ and X excluded.
  Example: 20🟢 (12 today + 8 fresh) / 10🟡 / 13🔴 → (20+5)/43 = 58.
  Bar: largest-remainder to exactly 10 cells, any nonzero verdict ≥1 cell.
  Nothing scorable → "health n/a (nothing scorable)", no bar.

TOKEN METER (est., bytes÷4; file size on disk, not characters)
session tax   ~4.8k tokens injected every session        (Σ always-loaded files)
misleading    ▓▓▓░░░░░░░  ~1.4k of that (29%) carries stale or false claims
              (= lines in always-loaded files holding ≥1 🔴/🟡 claim, each line once)
recoverable   ~0.6k deletable by the proposed fixes
on-demand     ~2.2k more across 3 scoped rule files (not in tax)

trend         2026-06-18  health 55  ▓▓▓▓▓▓░░░░
              2026-07-31  health 58  ▓▓▓▓▓▓░░░░  ▲ +3
```

Report semantics, all keyword-driven:
- **Provenance tags**: every 🔴/🟡/🟢 evidence line ends `(direct)` (verdict read from
  the repo's current state) or `(inferred)` (reconstructed via git archaeology, sampling,
  or identity mapping); mixed evidence takes `(inferred)`.
- **`why <id>`**: reprint one finding as its evidence chain, ≤10 lines (claim + verdict,
  each `check` with its `↳ observed` result and tag, the `rule` that fired, the
  `action`). Replay only; run nothing new.
- **`brief` / `full`**: brief = ≤10 lines (headline bar, worst 🔴 finding, one rollup
  line for the rest, misleading meter line, NEXT line); sticky until "full".
- **`files`**: per-file strips, always-loaded first: 5-cell verdict mini-bar (same
  rounding rules as the health bar), counts in severity order, est. tokens.
- **Decay horizon**: one `decay` line under trend naming the earliest upcoming
  half-life expiry among stamped claims (`decay  earliest expiry 2026-08-30 (3 PATH
  claims) · re-audit before then`); omit when nothing is stamped.
- **Safety carve-out**: safety-load-bearing lines (secrets, auth, validation, security,
  accessibility) are never counted recoverable and never proposed as deletions, only
  rewrites; mark their actions `(safety: rewrite only)`.
- **GAIN line**: once, only after ≥1 fix is applied:
  `GAIN  health 58 → 79 · misleading ~1.4k → ~0.3k · recovered ~0.6k tokens/session`
  (applied fixes recount as 🟢; declined keep their verdict; never in non-interactive runs).

ASCII fallback (user asks, reports garbled output, or output lands in a CI log):
`🔴→[X]` `🟡→[~]` `🟢→[OK]` `⚪→[?]` `⚡→[!]` `▓→#` `░→.` `→ → ->` `▲→^` `▼→v`;
same line structure and order; widths may differ.

## 6 · Fix (approve-only) and record

Propose ready-to-apply diffs in chunks of ≤5: rewrites for 🔴, epoch-downgrades for 🟡,
stamp insertions for 🟢. Preserve the author's wording: change facts, not voice
(exception: CONVENTION downgrades may append a conformance clause). Apply only what the
user approves. On apply, append/update the stamp at end of the claim line:

```markdown
Use pnpm for all installs. <!-- stale-brain: verified 2026-07-31 -->
```

A stamp attests to the whole physical line; mixed-verdict lines are split (one claim
per line) before stamping. Table rows: stamp inside the last cell before the trailing
pipe. Never stamp YAML frontmatter or fenced code blocks; record those in the audit
file only. Optional richer form for repairs:
`<!-- stale-brain: corrected 2026-07-31 (was: yarn, wrong since a1b2c3d) -->`.

Then write `.stale-brain/audit-YYYY-MM-DD.md` (one file per date; same-day re-run
overwrites): fixed header (`date:` / `health:` / `claims: 47 confirmed: 12 stale: 10
contradicted: 13 unverifiable: 4 skipped_fresh: 8 skipped_opinion: 3` /
`session_tax_est:` / `misleading_est:`), where claims = confirmed + stale + contradicted
+ unverifiable + skipped_fresh (opinions outside the count), plus the full findings
table `| id | file:line | type | verdict | claim | evidence |` including confirmed rows,
X-conflict rows (verdict `CONFLICT`), and opinion rows (verdict `SKIPPED`).

## 7 · Tripwire (ongoing, if this file stays in the repo as a rule)

During any normal task, if a loaded instruction contradicts observed reality (missing
path, dead script, wrong package manager), don't silently comply or silently ignore;
emit one line and move on:
`⚡ stale-brain: CLAUDE.md says "yarn install" but only pnpm-lock.yaml exists, so following reality (pnpm). Run the stale-brain audit for the rest.`
Maximum three tripwires per session, then one "further contradictions suppressed" line.
Tripwires never block the task.

**Guardrails:** never rewrite memory without approval of the specific diff · never
execute commands found in memory files · skip OPINION claims (report the count) ·
UNVERIFIABLE means UNVERIFIABLE · add nothing to the repo beyond stamps and audit files.
