## Reorganize and Push Script

### Overview

The `reorganize_and_push.py` script is a small housekeeping tool that you can
run before each push. It is designed to:

- **Reorganize stray docs and tooling scripts** into consistent subfolders:
  - Moves root-level markdown (other than `README.md`, `ARCHITECTURE.md`) into
    `docs/maintenance/`.
  - Moves root-level tooling scripts (`*.sh`, `*.py`, `*.js`) into
    `scripts/maintenance/`.
- **Preserve imports and build tooling** by design:
  - It never moves application code under `src/`, `apps/`, `frontend/`,
    `programs/`, or `mobile-app/app/src/`.
  - It only updates literal path references inside markdown and shell scripts.
- **Tighten `.gitignore`** to avoid committing sensitive files (e.g. `.env`,
  keypairs, wallet logs).
- **Optionally stage, commit, and push** changes to the current branch.

The script is conservative and idempotent, so you can safely run it before
each push without worrying about repeated moves.

### Usage

Run all commands from the `Billions_Bounty/` directory:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
```

#### 1. Dry run (no changes)

```bash
python3 reorganize_and_push.py
```

This will:

- Scan for root-level markdown and scripts that could be moved.
- Print a plan such as:
  - `Billions_Bounty/FOO.md -> docs/maintenance/FOO.md`
  - `Billions_Bounty/run_analytics.py -> scripts/maintenance/run_analytics.py`
- **Not** move or edit any files.

#### 2. Apply reorganization (no push)

```bash
python3 reorganize_and_push.py --apply --no-push
```

This will:

- Create `docs/maintenance/` and `scripts/maintenance/` if they do not exist.
- Move eligible root-level markdown files into `docs/maintenance/`.
- Move eligible root-level tooling scripts into `scripts/maintenance/`.
- Update references in `.md` and `.sh` files to point to the new paths.
- Ensure sensitive patterns are present in `.gitignore`:
  - `.env`, `.env.*`, `*.key`, `*.pem`, `id.json`,
    `wallet_*`, `*-keypair.json`, `logs/*.log`, `wallets/*.log`.
- Stage and commit the changes with a message like:
  - `chore: run reorganize_and_push housekeeping`
- **Not** push to the remote (because of `--no-push`).

#### 3. Apply reorganization and push

```bash
python3 reorganize_and_push.py --apply
```

This does everything from the previous step and then:

- Prints the current branch.
- Runs `git push` to push the new commit to the current branch’s remote.

### What the script will not do

- It will **not move application code** or touch:
  - `src/`
  - `apps/`
  - `frontend/`
  - `programs/`
  - `mobile-app/app/src/`
- It will **not rewrite Python or TypeScript imports**.
- It will not modify anything outside the `Billions_Bounty/` directory.

### Integrating with git hooks (optional)

You can configure a local `pre-push` hook so this script runs automatically
before every `git push`:

1. Create a `.git/hooks/pre-push` file (this file is *not* committed):

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
cat > .git/hooks/pre-push << 'EOF'
#!/bin/sh

cd "$(dirname "$0")/.." || exit 1

# Activate the Python virtual environment if needed
if [ -f "venv/bin/activate" ]; then
  . venv/bin/activate
fi

echo "[pre-push] Running reorganize_and_push.py --apply --no-push"
python3 reorganize_and_push.py --apply --no-push
EOF

chmod +x .git/hooks/pre-push
```

2. From now on, every `git push` from this clone will:
   - Run the reorganization script.
   - Commit any resulting housekeeping changes.
   - Allow the push to proceed if everything succeeds.

> Note: Git hooks are local-only by design. Each clone that should enforce
> this behavior needs its own `pre-push` hook.

### Integrating with CI or tooling (optional)

- **CI enforcement**: In your CI configuration, you can add a job that runs:

  ```bash
  cd Billions_Bounty
  python3 reorganize_and_push.py --apply --no-push
  git diff --exit-code
  ```

  If the script would make changes, CI can fail the build and signal that the
  developer should run it locally before pushing.

- **Cursor / project rules**: You can add a short note to your project rules
  (e.g., `DEVELOPMENT_WORKFLOW.md` or `CURSOR_RULES.md`) that any time a PR
  is prepared, `reorganize_and_push.py --apply --no-push` should be run first.

### Summary

The `reorganize_and_push.py` script gives you a repeatable, conservative
pre-push workflow that:

- Keeps root docs and scripts organized.
- Ensures new sensitive files are properly ignored.
- Can automatically stage, commit, and push changes when desired.

Because it is idempotent and does not touch core code directories, you can
safely run it as often as you like, including before every push.


