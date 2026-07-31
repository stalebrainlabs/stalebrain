# Output format: CALM output, Pulse graphs, token meter

stale-brain's terminal output follows one design system, defined here from scratch.
Two named parts: **CALM** (the writing rules) and **Pulse** (the graph primitives).
Everything renders as plain Unicode text (no libraries, no dependencies, no color
codes) so it renders identically in any UTF-8 terminal with an emoji-capable font;
for anything else there is a complete ASCII fallback below.

Every example in this file describes the same audit: a re-audit of a repo with 7 memory
files (4 always-loaded, ~4.8k tokens; 3 on-demand, ~2.2k), 47 claims = 12 confirmed
today + 10 stale + 13 contradicted + 4 unverifiable + 8 fresh-skipped, plus 3 opinions
outside the count. Keep any imitation of these examples just as self-consistent.

## CALM: the writing rules

CALM = **C**hunked · **A**ctionable · **L**ow-noise · **M**eaningful. Built for readers
who lose walls of text (and for the ones who just hate them). The rules are hard rules:

- **Chunked.** The initial report is one screen: each verdict section shows at most
  5 findings, overflow elided with `[first 5 of N]` and a section hand-off
  (`→ 8 more contradicted, say "next"`). The stop-and-wait mechanic applies to section
  overflow and to the fix flow. One idea per line; blank line between blocks. The
  confirmed list, if requested, is also chunked (≤10 per block).
- **Actionable.** Every finding line ends in what to do, not just what's wrong.
  Verdict first, evidence second, action third. No finding without a proposed action.
- **Low-noise.** No preamble, no "I will now…", no restating the request, no
  apologies. Progress is ticker lines only, at most one per ~10 claims per step.
  Confirmed claims are a count, not a list.
- **Meaningful.** Plain words. "Your CLAUDE.md says yarn; the lockfile says pnpm"
  beats "a package-manager inconsistency was detected". Numbers get units. Estimates are
  labeled estimates.

Symbol anchors, used consistently everywhere: 🔴 contradicted · 🟡 stale · 🟢 confirmed ·
⚪ unverifiable · ⚡ tripwire.

**ASCII fallback**: switch when the user asks for ASCII, reports garbled output, or
says the output lands in a CI log / legacy console (you cannot see their screen; the
first report may end with a one-time footer: `symbols garbled? say "ascii"`). Complete
mapping, same line structure and order (widths may differ):
`🔴→[X]` `🟡→[~]` `🟢→[OK]` `⚪→[?]` `⚡→[!]` `▓→#` `░→.` `→ → ->` `▲→^` `▼→v`.

## Pulse: graph primitives

Four primitives. Fixed widths, fixed formats, recognizable at a glance across runs.

**1. Health bar**: 10 cells, one cell ≈ 10% of scored claims, filled by verdict share
(🔴 first, then 🟡, then 🟢), score appended:

```
🔴🔴🔴🟡🟡🟢🟢🟢🟢🟢  health 58/100
```

- `health = (confirmed + 0.5 × stale) / (confirmed + stale + contradicted) × 100`, rounded.
- **`confirmed` includes fresh-skipped claims**: a valid stamp is a confirmation.
- ⚪ unverifiable claims are excluded from the score and reported separately: not
  knowing is not the same as being wrong. X-conflict findings are never scored.
- Cell rounding: largest remainder, exactly 10 cells, any nonzero verdict gets ≥1 cell.
  (Example: 13🔴/10🟡/20🟢 of 43 scored → 3.02/2.33/4.65 → 3/2/5 cells; health
  (20+5)/43 = 58.1 → 58.)
- No scorable claims at all → print `health n/a (nothing scorable)` with no bar.

**2. Meter**: 10-cell `▓░` bar for any part-of-whole quantity, fill = round(share × 10):

```
▓▓▓▓▓▓▓░░░  3.4k of 4.8k always-loaded tokens are sound (71%)
```

("sound" = session tax − misleading; 3.4/4.8 = 71% → 7 cells.)

**3. Trend**: one line per prior audit (parsed from `.stale-brain/audit-*.md` headers),
oldest first, max last 5, today last with a delta arrow. Rendered only when prior audits
exist; omit the block entirely on a first audit:

```
2026-05-02  health 41  ▓▓▓▓░░░░░░
2026-06-18  health 55  ▓▓▓▓▓▓░░░░
2026-07-31  health 58  ▓▓▓▓▓▓░░░░   ▲ +3
```

**4. Ticker**: the live progress line during steps 1–4 (the audit's "tail -f"). One
line per emission, prefixed `[stale-brain]`, at most one per ~10 claims per step, counts
in severity order 🔴🟡⚪🟢. Terminals driven by an agent can't redraw in place; the
ticker is append-only by design:

```
[stale-brain] inventory · 7 files (4 always-loaded ~4.8k + 3 on-demand ~2.2k)
[stale-brain] verifying 20/39 · 🔴6 🟡4 ⚪2 🟢8
[stale-brain] verifying 39/39 · 🔴13 🟡10 ⚪4 🟢12
```

(The ticker's inventory total covers *all* audited files; the session tax below covers
always-loaded only. 39 = 47 claims − 8 fresh-skipped.)

## Token meter

Memory files are a tax the user pays every session. The meter makes it visible.

- `est_tokens(file) = round(bytes / 4)`, where bytes = file size on disk (`wc -c`,
  PowerShell `(Get-Item f).Length`), not character count. Always labeled "~" and "est.";
  it's a ±20% English-text heuristic (worse on heavily non-English content; CRLF
  checkouts run ~1 byte/line higher, within tolerance), and honesty about that is part
  of the format.
- **Session tax** = Σ est_tokens over always-loaded files (per memory-sources.md
  classification; on-demand files listed separately, never summed into the tax).
- **Misleading** = est. tokens of lines *in always-loaded files* that contain at least
  one 🔴 or 🟡 claim, each physical line counted at most once, headings excluded,
  rounded once at the end. By construction it cannot exceed the session tax. Misleading
  tokens in on-demand files are reported on the on-demand line instead.
- **Recoverable** = est. tokens the proposed fixes would delete (dead sections, resolved
  duplications). Rewrites that stay the same length recover ~0 and the meter says so.

```
TOKEN METER  (est., bytes÷4)
session tax   ~4.8k tokens injected every session
misleading    ▓▓▓░░░░░░░  ~1.4k of that (29%) carries stale or false claims
recoverable   ~0.6k deletable by the proposed fixes
on-demand     ~2.2k more across 3 scoped rule files (not in tax; ~0.2k misleading there)
```

## The report template

Assembled in this exact order (CALM: worst first, detail on request). Empty verdict
sections are omitted entirely. `⋮` below marks template abridgement; a real report
fills each section to its cap:

```
STALE-BRAIN AUDIT · acme-web · 2026-07-31
🔴🔴🔴🟡🟡🟢🟢🟢🟢🟢  health 58/100 · 47 claims from 7 files (8 fresh-skipped, 3 opinions skipped)

🔴 CONTRADICTED · 13 (fix these first)   [first 5 of 13]
C7   CLAUDE.md:12   "use yarn for all installs"
     → pnpm-lock.yaml is the only lockfile since a1b2c3d (2026-03-14); packageManager: pnpm@9
     → fix: rewrite to pnpm
C31  AGENTS.md:8    "run npm test before committing"
     → no "test" script; scripts block has "test:unit" since e4f5a6b
     → fix: rewrite to pnpm test:unit
⋮
X1   CLAUDE.md:22 ↔ AGENTS.md:9   deploy target asserted as Vercel AND Netlify
     → no in-repo evidence for either → ask the user which is true

→ 8 more contradicted, say "next" to continue or "fixes" to jump to the diffs.

🟡 STALE · 10   [first 5 of 10]
C3   CLAUDE.md:9    "ask @maria about billing"  · no commits from @maria in 9 months; not in CODEOWNERS
     → fix: downgrade to "as of 2026-02, @maria owned billing" or name the current owner
C19  AGENTS.md:14   "error handling uses the Result type"  · 3 of 5 sampled files conform
     → fix: append conformance clause
⋮

⚪ UNVERIFIABLE · 4
C22  .cursorrules:4  "the payments team reviews schema changes" · no observable in-repo evidence
⋮

🟢 CONFIRMED · 12 verified today + 8 fresh (stamp within half-life) · stamped on apply · say "confirmed" for the chunked list

TOKEN METER  (est., bytes÷4)
session tax   ~4.8k tokens injected every session
misleading    ▓▓▓░░░░░░░  ~1.4k of that (29%) carries stale or false claims

trend         2026-06-18  health 55  ▓▓▓▓▓▓░░░░
              2026-07-31  health 58  ▓▓▓▓▓▓░░░░  ▲ +3

→ NEXT: "fixes" to review diffs (13 rewrites, 10 downgrades, 12 stamps) · "confirmed" to list 🟢 · "report" for the full table
```

The fix flow then presents diffs in chunks of ≤5, each diff preceded by its claim line,
each chunk ending with the approve hand-off. Nothing is applied without a yes. In
non-interactive runs (no human to answer): emit all chunks sequentially, apply nothing,
and record the diffs in the audit file as proposed-only.

## The audit file

`.stale-brain/audit-YYYY-MM-DD.md`: the machine-readable memory of the audit. One file
per date; a same-day re-run overwrites it. Header lines are fixed-format, one regex per
field, so future runs (and the trend graph) can parse them. The count identity:
`claims = confirmed + stale + contradicted + unverifiable + skipped_fresh`;
`skipped_opinion` sits outside the count (opinion rows do appear in the findings table
with verdict `SKIPPED`). For scoring, fresh-skipped count as confirmed.

```markdown
# stale-brain audit
date: 2026-07-31
health: 58
claims: 47 confirmed: 12 stale: 10 contradicted: 13 unverifiable: 4 skipped_fresh: 8 skipped_opinion: 3
session_tax_est: 4800
misleading_est: 1400

## findings
| id | file:line | type | verdict | claim | evidence |
|----|-----------|------|---------|-------|----------|
| C7 | CLAUDE.md:12 | DEP | CONTRADICTED | "use yarn for all installs" | pnpm-lock.yaml only lockfile since a1b2c3d; packageManager pnpm@9 |
| X1 | CLAUDE.md:22 ↔ AGENTS.md:9 | FACT | CONFLICT | deploy target: Vercel vs Netlify | no in-repo evidence for either |
| C40 | CLAUDE.md:31 | OPINION | SKIPPED | "prefer small functions" | - |
...
```

Full findings table (including confirmed and skipped rows) lives here, so the terminal
report can stay CALM.

## Stamps

```markdown
Use pnpm for all installs. <!-- stale-brain: verified 2026-07-31 -->
```

- HTML comments: invisible in every rendered markdown view, greppable as plain text
  (`stale-brain: verified`), and safely ignored by every agent that reads the file.
- A stamp attests to the **entire physical line** and is applied only when every claim
  on that line is confirmed. If a line carries claims with mixed verdicts, the fix first
  splits it (one claim per line), then stamps. For a sentence hard-wrapped across
  lines, the stamp goes at the end of its final physical line.
- One stamp per line, appended at end of line; re-verification updates the date in
  place. Never stack stamps.
- Table-row claims: place the stamp inside the last cell, before the trailing pipe
  (`| … claim <!-- stale-brain: verified 2026-07-31 --> |`). Never stamp lines inside
  YAML frontmatter or fenced code blocks; record those claims' provenance in the audit
  file only.
- Optional richer form for repaired lines, preserving the wrong-since provenance the
  audit dug up: `<!-- stale-brain: corrected 2026-07-31 (was: yarn, wrong since a1b2c3d) -->`.
  Age is measured from the date in either stamp form.
- A downgraded STALE claim carries its epoch in prose instead: "as of 2026-02, X was
  true"; the honesty is in the text, where every model reading the file benefits, not
  only ones that know stale-brain.
