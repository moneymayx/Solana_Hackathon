#!/usr/bin/env python3
"""
Reorganize and Push Script
--------------------------

This script performs four main tasks for the Billions Bounty codebase:

1. **Reorganize stray markdown and tooling scripts** into structured subfolders:
   - Markdown files at the repo root (except a small allowlist) are moved into
     `docs/maintenance/`.
   - Root-level tooling scripts (`*.sh`, `*.py`, `*.js`) are moved into
     `scripts/maintenance/` (or other script subfolders in future iterations).

2. **Preserve imports and script call sites** by design:
   - It never moves application source code under `src/`, `apps/`, `frontend/`,
     `programs/`, or `mobile-app/app/src/`.
   - It only updates references to moved files inside markdown and shell
     scripts, where paths are simple literals.

3. **Ensure sensitive files are ignored by git** by appending safe patterns
   to `.gitignore` if they are missing (e.g. `.env*`, `*-keypair.json`, etc.).

4. **Optionally stage, commit, and push** changes to the current branch.

Usage (from `Billions_Bounty/`):

    # Dry run (no changes)
    python3 reorganize_and_push.py

    # Apply moves + .gitignore updates, but do NOT push
    python3 reorganize_and_push.py --apply --no-push

    # Apply moves + .gitignore updates, then stage, commit, and push
    python3 reorganize_and_push.py --apply

The script is intentionally conservative and idempotent so you can run it
before each push as a housekeeping step.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


REPO_ROOT = Path(__file__).resolve().parent


DOCS_ROOT = REPO_ROOT / "docs"
SCRIPTS_ROOT = REPO_ROOT / "scripts"

DOCS_MAINTENANCE = DOCS_ROOT / "maintenance"
SCRIPTS_MAINTENANCE = SCRIPTS_ROOT / "maintenance"

# Mobile app roots – used to keep mobile scripts/docs organized under mobile-app/.
MOBILE_ROOT = REPO_ROOT / "mobile-app"
MOBILE_DOCS_ROOT = MOBILE_ROOT / "docs"
MOBILE_SCRIPTS_ROOT = MOBILE_ROOT / "scripts"
MOBILE_DOCS_MAINTENANCE = MOBILE_DOCS_ROOT / "maintenance"


SCRIPT_EXTENSIONS = {".sh", ".py", ".js"}
DOC_EXTENSIONS = {".md"}


# Directories that should never be traversed or affected by moves.
IGNORE_DIR_NAMES = {
    ".git",
    "venv",
    "node_modules",
    "target",
    ".pytest_cache",
    "__pycache__",
    ".idea",
    ".vscode",
    "dist",
    "build",
}

# Code roots that must remain untouched to avoid breaking imports/builds.
CODE_ROOT_PREFIXES = {
    "src",
    "apps",
    "frontend",
    "programs",
    "mobile-app/app/src",
}

# Markdown files to keep at the root of Billions_Bounty.
ROOT_MD_ALLOWLIST = {
    "README.md",
    "ARCHITECTURE.md",
}


SENSITIVE_GITIGNORE_PATTERNS = [
    "# Added by reorganize_and_push.py – sensitive keys & envs",
    ".env",
    ".env.*",
    "*.key",
    "*.pem",
    "id.json",
    "wallet_*",
    "*-keypair.json",
    "logs/*.log",
    "wallets/*.log",
]


@dataclass
class MovePlan:
    src: Path
    dest: Path


def is_under_code_root(path: Path) -> bool:
    """Return True if the path resides under a code root that we never move."""
    try:
        rel = path.relative_to(REPO_ROOT)
    except ValueError:
        return False

    parts = rel.parts
    if not parts:
        return False

    prefix = parts[0]
    # Special handling for nested mobile app code root.
    if prefix == "mobile-app" and len(parts) >= 3 and parts[1] == "app" and parts[2] == "src":
        return True

    if prefix in CODE_ROOT_PREFIXES:
        return True

    return False


def iter_files(root: Path) -> Iterable[Path]:
    """Yield all files under root, skipping ignored directories."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in-place.
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIR_NAMES]
        for filename in filenames:
            yield Path(dirpath) / filename


def find_move_candidates() -> Tuple[List[MovePlan], List[MovePlan]]:
    """
    Identify markdown and script files that should be moved.

    Returns:
        (doc_moves, script_moves)
    """
    doc_moves: List[MovePlan] = []
    script_moves: List[MovePlan] = []

    for path in iter_files(REPO_ROOT):
        # Skip this script and its README; they are intentionally at the root.
        if path == REPO_ROOT / "reorganize_and_push.py":
            continue
        if path.name == "REORGANIZE_AND_PUSH.md":
            continue

        # Never move files under code roots.
        if is_under_code_root(path):
            continue

        rel = path.relative_to(REPO_ROOT)
        ext = path.suffix.lower()

        # Markdown candidates: only those at the repo root (e.g. Billions_Bounty/*.md).
        if ext in DOC_EXTENSIONS and len(rel.parts) == 1:
            if path.name not in ROOT_MD_ALLOWLIST and not path.name.startswith("."):
                dest = DOCS_MAINTENANCE / path.name
                doc_moves.append(MovePlan(src=path, dest=dest))
            continue

        # Mobile-app markdown candidates: /mobile-app/*.md -> mobile-app/docs/maintenance/.
        if ext in DOC_EXTENSIONS and len(rel.parts) == 2 and rel.parts[0] == "mobile-app":
            name = rel.parts[1]
            if name != "README.md" and not name.startswith("."):
                dest = MOBILE_DOCS_MAINTENANCE / name
                doc_moves.append(MovePlan(src=path, dest=dest))
            continue

        # Script candidates: root-level tooling scripts only.
        if ext in SCRIPT_EXTENSIONS and len(rel.parts) == 1:
            # Skip obvious project entrypoints or this script itself.
            if path.name in {"manage.py", "setup.py"}:
                continue
            dest = SCRIPTS_MAINTENANCE / path.name
            script_moves.append(MovePlan(src=path, dest=dest))
            continue

        # Mobile-app script candidates: /mobile-app/*.sh|*.py|*.js -> mobile-app/scripts/.
        if ext in SCRIPT_EXTENSIONS and len(rel.parts) == 2 and rel.parts[0] == "mobile-app":
            name = rel.parts[1]
            dest = MOBILE_SCRIPTS_ROOT / name
            script_moves.append(MovePlan(src=path, dest=dest))
            continue

    return doc_moves, script_moves


def ensure_directories() -> None:
    """Create maintenance directories if they do not exist."""
    DOCS_MAINTENANCE.mkdir(parents=True, exist_ok=True)
    SCRIPTS_MAINTENANCE.mkdir(parents=True, exist_ok=True)
    # Mobile-app maintenance directories (for root-level mobile docs/scripts).
    if MOBILE_ROOT.exists():
        MOBILE_DOCS_MAINTENANCE.mkdir(parents=True, exist_ok=True)
        MOBILE_SCRIPTS_ROOT.mkdir(parents=True, exist_ok=True)


def apply_moves(moves: List[MovePlan]) -> None:
    """Perform file moves as described in the move plans."""
    for plan in moves:
        plan.dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"[MOVE] {plan.src.relative_to(REPO_ROOT)} -> {plan.dest.relative_to(REPO_ROOT)}")
        shutil.move(str(plan.src), str(plan.dest))


def build_reference_map(moves: List[MovePlan]) -> Dict[str, str]:
    """
    Build a mapping of old relative paths to new relative paths for search/replace.
    Only used for markdown and shell scripts where path literals are common.
    """
    mapping: Dict[str, str] = {}
    for plan in moves:
        old_rel = plan.src.relative_to(REPO_ROOT).as_posix()
        new_rel = plan.dest.relative_to(REPO_ROOT).as_posix()
        mapping[old_rel] = new_rel
    return mapping


def update_references(ref_map: Dict[str, str]) -> None:
    """
    Update references to moved files in markdown and shell scripts.

    This only edits `.md` and `.sh` files, and only replaces literal path
    substrings for the old relative paths. It does not attempt to update import
    statements in Python/TypeScript.
    """
    if not ref_map:
        return

    candidates: List[Path] = []
    for path in iter_files(REPO_ROOT):
        if path.suffix.lower() in {".md", ".sh"}:
            candidates.append(path)

    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        original_text = text
        for old_rel, new_rel in ref_map.items():
            text = text.replace(old_rel, new_rel)
            # Also handle leading ./ usage in shell snippets.
            text = text.replace(f"./{old_rel}", f"./{new_rel}")

        if text != original_text:
            print(f"[UPDATE] references in {path.relative_to(REPO_ROOT)}")
            path.write_text(text, encoding="utf-8")


def ensure_gitignore_patterns() -> None:
    """Append sensitive patterns to .gitignore if they are not already present."""
    gitignore_path = REPO_ROOT / ".gitignore"
    if not gitignore_path.exists():
        print("[INFO] .gitignore not found at repo root; skipping sensitive pattern update.")
        return

    content = gitignore_path.read_text(encoding="utf-8").splitlines()
    existing = set(content)

    added_any = False
    for pattern in SENSITIVE_GITIGNORE_PATTERNS:
        if pattern not in existing:
            content.append(pattern)
            added_any = True

    if added_any:
        print("[GITIGNORE] Appending sensitive file patterns to .gitignore")
        gitignore_path.write_text("\n".join(content) + "\n", encoding="utf-8")


def run_git(args: List[str]) -> Tuple[int, str]:
    """Run a git command in the repo root and return (exit_code, stdout)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(REPO_ROOT),
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return result.returncode, result.stdout.strip()
    except FileNotFoundError:
        print("[WARN] git not found on PATH; skipping git integration.")
        return 1, ""


def git_status_porcelain() -> str:
    code, out = run_git(["status", "--porcelain"])
    if code != 0:
        return ""
    return out


def git_add_all() -> None:
    code, out = run_git(["add", "."])
    if code != 0:
        print("[WARN] git add failed:")
        print(out)


def git_commit(message: str) -> None:
    code, out = run_git(["commit", "-m", message])
    if code != 0:
        print("[WARN] git commit failed (possibly no changes to commit):")
        print(out)


def git_push() -> None:
    # Print branch and remote for clarity.
    _, branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    print(f"[GIT] Pushing current branch: {branch}")
    code, out = run_git(["push"])
    if code != 0:
        print("[WARN] git push failed:")
        print(out)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reorganize docs/scripts, update .gitignore, and optionally commit & push."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply moves and .gitignore updates (default is dry-run only).",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Do not push changes even if --apply is set.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    print(f"[INFO] Repo root: {REPO_ROOT}")

    ensure_directories()

    doc_moves, script_moves = find_move_candidates()

    if not doc_moves and not script_moves:
        print("[INFO] No candidates found for reorganization.")
    else:
        print("[PLAN] Proposed moves:")
        for plan in doc_moves + script_moves:
            print(f"  - {plan.src.relative_to(REPO_ROOT)} -> {plan.dest.relative_to(REPO_ROOT)}")

    if not args.apply:
        print("\n[DRY RUN] No changes have been made. Re-run with --apply to apply this plan.")
        return 0

    # Apply moves.
    if doc_moves or script_moves:
        apply_moves(doc_moves + script_moves)
        # Update references in markdown and shell scripts.
        ref_map = build_reference_map(doc_moves + script_moves)
        update_references(ref_map)

    # Ensure sensitive patterns are in .gitignore.
    ensure_gitignore_patterns()

    # Git integration.
    status = git_status_porcelain()
    if not status:
        print("[INFO] No git changes to commit.")
        return 0

    print("[GIT] Pending changes:\n" + status)
    git_add_all()
    git_commit("chore: run reorganize_and_push housekeeping")

    if not args.no_push:
        git_push()
    else:
        print("[GIT] Skipping push due to --no-push flag.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


