# Agent Briefing

This is the copyable operating brief for coding agents entering The Compound.

## Trey

- Worktree: `D:\The_Compound_Worktrees\Trey`
- Branch: `trey/workspace`
- Dev HUD: `http://127.0.0.1:8766`

## Joe

- Worktree: `D:\The_Compound_Worktrees\Joe`
- Branch: `joe/workspace`
- Dev HUD: `http://127.0.0.1:8767`

## Live Compound

- Live app folder: `D:\The_Compound`
- Live local HUD: `http://127.0.0.1:8765`
- Live Tailscale HUD: `http://100.87.143.16:8765`

Keep the live app running on the side while worktree dev servers run on their own ports.

## Push And Merge

1. Work only in your operator worktree.
2. Pull from `master` before starting new work.
3. Run tests before committing.
4. Push to your own branch.
5. Merge to `master` only after review/checks.
6. Update the live folder after the merge.

## Conflict Rules

- Stop and inspect both versions.
- Keep intentional work from both operators.
- Do not overwrite the other operator's branch.
- Resolve conflicts in the worktree, rerun tests, and commit the resolution.
- Ask Trey/Joe if the right resolution is unclear.
