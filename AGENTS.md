# The Compound Agent Instructions

Use this file first when an agent is asked to work on The Compound.

## Worktrees

- Live shared app: `D:\The_Compound`
- Trey worktree: `D:\The_Compound_Worktrees\Trey`
- Trey branch: `trey/workspace`
- Trey dev HUD: `http://127.0.0.1:8766`
- Joe worktree: `D:\The_Compound_Worktrees\Joe`
- Joe branch: `joe/workspace`
- Joe dev HUD: `http://127.0.0.1:8767`
- Live HUD: `http://127.0.0.1:8765` locally or `http://100.87.143.16:8765` over Tailscale

## Rules

- Do feature work in the operator worktree, not in `D:\The_Compound`.
- Keep `D:\The_Compound` available as the live shared server on port `8765`.
- Use Trey dev on port `8766` and Joe dev on port `8767`.
- Commit focused source/docs/test changes from the worktree.
- Push to the matching branch with `git push origin trey/workspace` or `git push origin joe/workspace`.
- Merge to `master` only after tests pass and the change is reviewed.
- If merge conflicts appear, stop and inspect both sides. Keep intentional work from both operators. Ask before deleting or overwriting another operator's work.
- Do not commit ignored runtime state such as `data/board.json`, logs, or local process files unless Trey explicitly asks.

## Merge Loop

1. `git fetch origin`
2. `git merge --ff-only origin/master`
3. Make the change in the worktree.
4. Run `python -m unittest discover -s tests`.
5. `git status --short`
6. `git add <intentional files>`
7. `git commit -m "<clear message>"`
8. `git push origin <operator branch>`
9. Open or request a PR into `master`.
10. After merge, update `D:\The_Compound` and restart the live server if needed.
