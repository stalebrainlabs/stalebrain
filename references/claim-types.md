# Claim types — taxonomy, half-lives, verification recipes

A **claim** is any statement in a memory file that reality could confirm or deny.
Split compound sentences into one claim each. If a sentence tells the agent to *do*
something, the claim is the factual premise behind it ("run `npm test`" claims that an
`npm test` script exists).

## Taxonomy and half-lives

Half-life = the age past which a claim's last verification stops being trusted. Passing
it (or churned evidence) *triggers* re-verification; the verdict is the re-verification
outcome — 🟢 if it confirms, 🔴 if disproven, 🟡 only when the check comes back
inconclusive (then the claim is downgraded from fact to hypothesis).

Defaults below; users can override per repo with a `## stale-brain config` section in any
audited file. Grammar: one directive per line, `half-life <TYPE>: <N>d` — days only,
TYPE uppercase from this taxonomy. Unknown or malformed lines are reported and ignored.
If multiple files configure the same type, the strictest (smallest) value wins. Never
extract claims from a config section.

| Type | What it claims | Half-life | Rationale |
|---|---|---|---|
| PATH | A file/directory exists ("components live in `src/ui/`") | 30d | paths churn fastest |
| SCRIPT | A named command/script/target exists ("run `npm test`") | 30d | scripts blocks churn with tooling |
| SYMBOL | A named function/class/component exists ("auth goes through `validateSession()`") | 45d | renames are common, slower than paths |
| DEP | A dependency, version, or package manager ("we use yarn", "React 18") | 60d | lockfiles change in bursts |
| FACT | Other checkable assertions ("we deploy on Vercel", "API is REST") | 90d | infra facts move slowly |
| OWNER | A person/team owns an area ("ask @maria about billing") | 90d | people leave quietly |
| CONVENTION | The code follows a pattern ("all API calls go through `apiClient`") | 120d | conventions erode gradually |
| OPINION | Style preference with no ground truth ("prefer small functions") | — | **skipped, never judged** |

Age is measured from the claim's last `<!-- stale-brain: verified YYYY-MM-DD -->` stamp;
an unstamped claim's age is unknown — treat it as *at* its half-life (eligible for
verification, not auto-STALE) on the first audit.

## Verification recipes

All git commands are read-only. Mind shell quoting: pickaxe (`-S`) patterns containing
double quotes must be single-quoted to survive both Git Bash and PowerShell 7 (legacy
PowerShell 5.1 may still mangle embedded quotes). Never execute the scripts/commands a
claim names — verify definitions only.

### PATH
1. Glob for the path. Exists → 🟢.
2. Missing → find the commit where it vanished: `git log --oneline -- <path>` (the most
   recent commit touching the dead name). For single files `--follow` may be added;
   `--follow` takes exactly one file and adds nothing for directories.
3. Recover the destination: `git log --oneline --name-status -1 <commit>` (no pathspec)
   — an `R100  old  new` line is a rename and supplies the new path for the rewrite; a
   `D  old` line is a deletion. Renamed → 🔴 with the rename commit cited and the new
   path in the rewrite. Deleted → 🔴 with the deletion commit. No git history at all →
   ⚪ (say why).

### SCRIPT
1. Look up the definition: `package.json` `scripts` block, `Makefile` / `justfile` /
   `Taskfile.yml` targets, `composer.json` scripts, or CI workflow steps
   (`.github/workflows/*.yml`).
2. Defined and matching → 🟢. Defined but different ("`npm test`" but the script is
   `test:unit`) → 🔴 citing the scripts block. Absent everywhere → 🔴; cite when it was
   removed with a pickaxe like `git log -S '"test":' --oneline -5 -- package.json`
   (single-quoted — see the quoting note above).
3. The proposed rewrite must invoke the script with the package manager the same
   audit's DEP verdicts established (`pnpm test:unit`, not `npm run test:unit`, in a
   pnpm repo).

### SYMBOL
1. Grep for the definition (declaration patterns for the repo's language).
2. Found → 🟢. Not found → `git log -S "<symbol>" --oneline -5` to locate the removal or
   rename commit → 🔴 with that commit cited. Pickaxe finds nothing → ⚪.
3. Recover the replacement name for the rewrite: `git log -p -S "<symbol>" -1` (or
   `git show <commit> -- <file>`) and take the added-line counterpart of the removed
   definition. No clear counterpart → cite the removal only and mark the rewrite "removed
   in <commit>; no replacement found".

### DEP
1. Package-manager claims: lockfile presence decides — `pnpm-lock.yaml`, `yarn.lock`,
   `package-lock.json`, `bun.lockb`; check the `packageManager` field in `package.json`
   and CI install steps as tiebreakers. Multiple lockfiles present → report the conflict
   itself; the `packageManager` field wins if set.
2. Dependency/version claims: check the manifest (`package.json`, `pyproject.toml`,
   `requirements.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`). Version
   claims compare against the manifest's constraint, not the lockfile's resolution,
   unless the claim is about the exact installed version.
3. Wrong → 🔴 citing the lockfile/manifest lines; `git log --oneline -3 -- <lockfile>`
   supplies the "since when" commit.

### FACT
1. Reduce to a checkable proxy: "we deploy on Vercel" → `vercel.json` / `.vercel/`;
   "monorepo managed by turborepo" → `turbo.json`; "API is REST under src/api" → treat
   as PATH + sample the handlers.
2. No mechanical proxy exists ("the payments team reviews all schema changes") → ⚪ with
   the reason "no observable evidence in-repo". Never guess.

### OWNER
1. Check `CODEOWNERS` (at `.github/CODEOWNERS`, `CODEOWNERS`, or `docs/CODEOWNERS`) for
   the named person/team on the claimed area. CODEOWNERS naming a *different* owner →
   🔴 citing the CODEOWNERS line.
2. Check recent activity: `git shortlog -sn HEAD --since="9 months ago" -- <area-path>`.
   Caution: shortlog returns git author names/emails, not GitHub handles. Map a claimed
   handle heuristically (`git log --author=<handle>` matches name and email substrings).
3. Named in CODEOWNERS, or identity maps and is active → 🟢. Identity maps but inactive
   → 🟡 ("no commits from @maria in 9 months; not in CODEOWNERS") — people leaving is
   decay, not contradiction. No CODEOWNERS *and* the handle cannot be mapped to any git
   identity → ⚪ with reason "cannot map handle to a git identity".

### CONVENTION
1. Identify the files the convention governs; sample 3–5 representative ones (recent +
   old, different subdirectories).
2. Grep each for conformance, and verdict in sample terms (percentages overstate what
   3–5 files can prove): **all** sampled files conform → 🟢 (note the sample size); a
   **majority but not all** → 🟡 with counter-example file:line; a **minority** → 🔴 with
   counter-examples cited — the convention is aspirational, and the rewrite should say so
   ("historically enforced; 1 of 4 sampled files conform as of 2026-07").

### Drift pass (all stamped claims)
`git log --oneline --since=<stamp-date> -- <every path the claim's evidence touched>`.
Empty → the stamp stands, skip the claim (count it as fresh). Non-empty → re-verify in
full; the touching commits go into the citation either way. Caveat: `--since` filters on
commit dates, so rebased/cherry-picked history can slip past, and a shallow clone
returns empty for everything — if `git rev-parse --is-shallow-repository` says true,
re-verify instead of trusting an empty drift pass.

## Extraction discipline

- Number claims `C1…Cn` in file order; keep the file:line anchor for each.
- The claim text in the report is a faithful short quote, not a paraphrase.
- A sentence can yield claims of different types; split rather than blend.
- When a claim is conditional ("if you touch billing, ask @maria"), verify the factual
  parts (OWNER: @maria owns billing) and leave the conditional logic alone.
- Do not manufacture claims from headings, code fences, or the stale-brain config
  section itself.
