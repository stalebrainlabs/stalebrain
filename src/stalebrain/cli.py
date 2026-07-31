"""stalebrain CLI: install the skill into Claude Code, or print the portable protocol.

Zero dependencies. Works the same from a PyPI/uv install or a git checkout.
"""

import argparse
import shutil
import sys
from pathlib import Path

from . import __version__

SKILL_FILES = ["SKILL.md", "PORTABLE.md"]
REFERENCE_FILES = [
    "references/memory-sources.md",
    "references/claim-types.md",
    "references/output-format.md",
]


def asset_root() -> Path:
    """Locate the skill files, whether installed as a wheel or run from a checkout."""
    packaged = Path(__file__).resolve().parent / "assets"
    if (packaged / "SKILL.md").is_file():
        return packaged
    checkout = Path(__file__).resolve().parents[2]
    if (checkout / "SKILL.md").is_file():
        return checkout
    sys.exit("stalebrain: skill files not found (broken install?)")


def cmd_install(args: argparse.Namespace) -> None:
    if args.project is not None:
        base = Path(args.project).resolve()
        if not base.is_dir():
            sys.exit(f"stalebrain: not a directory: {base}")
        dest = base / ".claude" / "skills" / "stale-brain"
        scope = "project"
    else:
        dest = Path.home() / ".claude" / "skills" / "stale-brain"
        scope = "user (all repos, CLI and desktop app)"

    src = asset_root()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "references").mkdir(exist_ok=True)
    for rel in SKILL_FILES + REFERENCE_FILES:
        shutil.copyfile(src / rel, dest / rel)

    print(f"[stale-brain] installed -> {dest}  ({scope})")
    print('[stale-brain] try: /stale-brain  (or say "audit my agent memory")')


def cmd_portable(_args: argparse.Namespace) -> None:
    text = (asset_root() / "PORTABLE.md").read_text(encoding="utf-8")
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8"))


def cmd_path(_args: argparse.Namespace) -> None:
    print(asset_root())


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="stalebrain",
        description="Provenance and decay for AI agent memory.",
    )
    parser.add_argument("--version", action="version", version=f"stalebrain {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_install = sub.add_parser("install", help="install the skill for Claude Code")
    p_install.add_argument(
        "--project",
        nargs="?",
        const=".",
        default=None,
        metavar="DIR",
        help="install into DIR/.claude/skills (default: user-level ~/.claude/skills)",
    )
    p_install.set_defaults(func=cmd_install)

    p_portable = sub.add_parser(
        "portable",
        help="print PORTABLE.md for any other agent (pipe it, or paste it into a chat)",
    )
    p_portable.set_defaults(func=cmd_portable)

    p_path = sub.add_parser("path", help="print where the skill files live")
    p_path.set_defaults(func=cmd_path)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
