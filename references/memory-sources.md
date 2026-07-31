# Memory sources: where every agent keeps its brain

stale-brain audits *agent-facing* instruction and memory files. This map is the
inventory checklist for step 1. Glob for all of them; report only what exists.

## Source map

| Agent / tool | Files (repo-relative unless noted) | Loading |
|---|---|---|
| Claude Code | `CLAUDE.md` (root **and** any subdirectory), `CLAUDE.local.md`, `.claude/**/*.md` (memory, rules, decision records), `~/.claude/CLAUDE.md` (user-global; audit only if user opts in) | always-loaded (root chain); `.claude/` memory varies |
| OpenAI Codex / cross-tool standard | `AGENTS.md` (root and any subdirectory) | always-loaded |
| Cursor | `.cursorrules` (legacy), `.cursor/rules/**/*.mdc` | always or glob-scoped (check each rule's frontmatter `globs`/`alwaysApply`) |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` | always-loaded / glob-scoped |
| Gemini CLI | `GEMINI.md` (root and subdirectories) | always-loaded |
| Windsurf | `.windsurfrules`, `.windsurf/rules/**` | always-loaded |
| Cline | `.clinerules` (file or directory `.clinerules/**`) | always-loaded |
| Roo Code | `.roo/rules/**` | always-loaded |
| Aider | `CONVENTIONS.md` (when referenced from `.aider.conf.yml`; check the conf) | opt-in |
| Zed | `.rules` | always-loaded |
| Amazon Q Developer | `.amazonq/rules/**` | always-loaded |
| JetBrains Junie | `.junie/guidelines.md` | always-loaded |
| OpenHands | `.openhands/microagents/repo.md`, other `.openhands/microagents/*.md` | always / trigger-scoped |
| Generic / project-specific | any file the user names ("also audit docs/agent-notes.md") | as stated |

Unknown agents appear constantly. The fallback heuristic: a markdown/text file whose
audience is *the agent* (imperative instructions about the repo) is in scope if the user
confirms it; a file whose audience is *humans* is not.

## Always-loaded vs on-demand

This classification drives the token meter. **Always-loaded** files are injected into
every session; their tokens are a per-session tax, and stale claims in them do
per-session damage. **On-demand** files (glob-scoped rules, opt-in docs) cost tokens only
when triggered; weight them accordingly and say so in the meter.

When loading behavior is ambiguous (e.g. a `.cursor/rules/*.mdc` without frontmatter),
classify as always-loaded (the conservative direction for a cost meter) and mark it
with `†` in the inventory table.

## Deliberately out of scope (unless the user asks)

- `README.md`, `CONTRIBUTING.md`, `docs/**`: human documentation. Auditing docs is a
  different (bigger) job; naming these in the report as "not audited" is fine, judging
  them is not.
- Lockfiles, manifests, CI configs: these are *evidence*, not memory. They are what
  claims get checked against.
- Prompt/transcript archives (`.specstory/`, session logs): history, not instructions.

## Cross-file conflict rule

During extraction, index claims by topic (package manager, test command, directory
layout, owner). Two memory files asserting different values for the same topic is a
conflict finding. Agents that read both files are being told two different truths; that
is worse than one stale file. Mechanics:

- **IDs and anchors.** Conflicts are numbered `X1…Xn` (separate from claim IDs) and
  anchored to both sides: `CLAUDE.md:12 ↔ .cursorrules:3`.
- **Not counted.** X-findings are excluded from the claim counts and the health score;
  the underlying claims are already scored individually.
- **Folding.** When verification already flags one or both sides (🔴/🟡), fold the
  conflict into those findings' evidence lines ("also conflicts with .cursorrules:3")
  instead of rendering a third finding. Render a standalone X-finding only when neither
  side is individually flagged (typically both ⚪: two files disagree and the repo offers
  no evidence either way); its action is "ask the user which is true", and it appears at
  the end of the 🔴 section.
