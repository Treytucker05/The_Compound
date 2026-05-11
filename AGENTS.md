# The Compound Agent Instructions

Read this file first whenever an agent enters any The Compound folder.

The goal is simple: keep the live shared Compound running, do coding work in
the correct operator worktree, verify in a browser, commit only intentional
changes, and never overwrite the other operator's work.

## Server Map

- Live shared app
  - Path: `D:\The_Compound`
  - Branch: `master`
  - Scheduled task: `TheCompoundServer`
  - Port: `8765`
  - Local URL: `http://127.0.0.1:8765/`
  - Tailscale URL: `http://100.87.143.16:8765/`

- Trey dev app
  - Path: `D:\The_Compound_Worktrees\Trey`
  - Branch: `trey/workspace`
  - Scheduled task: `TheCompoundTreyDev`
  - Port: `8766`
  - Local URL: `http://127.0.0.1:8766/`
  - Tailscale URL: `http://100.87.143.16:8766/`

- Joe dev app
  - Path: `D:\The_Compound_Worktrees\Joe`
  - Branch: `joe/workspace`
  - Scheduled task: `TheCompoundJoeDev`
  - Port: `8767`
  - Local URL: `http://127.0.0.1:8767/`
  - Tailscale URL: `http://100.87.143.16:8767/`

## First Move For Any Agent

Server checks and scheduled-task commands run on the desktop host
`desktop-9i7bgil`. If the agent is running on Joe's laptop instead of the
desktop, run those commands through SSH:

```bat
ssh treyt@desktop-9i7bgil "<command>"
```

1. Identify the operator.
   - Trey work goes in `D:\The_Compound_Worktrees\Trey`.
   - Joe work goes in `D:\The_Compound_Worktrees\Joe`.
   - Do not do feature work directly in `D:\The_Compound`; that folder is the
     live shared app.

2. Check git state before changing anything.

```bat
cd /d D:\The_Compound_Worktrees\Joe
git status --short --branch
```

Use the matching worktree path for Trey.

3. Check whether the servers are running.

```powershell
Get-NetTCPConnection -LocalPort 8765,8766,8767 -State Listen -ErrorAction SilentlyContinue |
  Select-Object LocalAddress,LocalPort,OwningProcess |
  Sort-Object LocalPort
```

Expected ports:
- `8765` live shared app
- `8766` Trey dev
- `8767` Joe dev

4. Start any missing server with its scheduled task.

```powershell
Start-ScheduledTask -TaskName TheCompoundServer
Start-ScheduledTask -TaskName TheCompoundTreyDev
Start-ScheduledTask -TaskName TheCompoundJoeDev
```

If only Joe is working, make sure at least `TheCompoundServer` and
`TheCompoundJoeDev` are running. If only Trey is working, make sure at least
`TheCompoundServer` and `TheCompoundTreyDev` are running.

5. Verify HTTP after starting servers.

```bat
curl.exe -sS --max-time 5 -o NUL -w "live 8765 %{http_code}\n" http://127.0.0.1:8765/
curl.exe -sS --max-time 5 -o NUL -w "trey 8766 %{http_code}\n" http://127.0.0.1:8766/
curl.exe -sS --max-time 5 -o NUL -w "joe 8767 %{http_code}\n" http://127.0.0.1:8767/
```

Expected result for running servers: `200`.

## Browser Login Checklist

Use the browser or computer-use tool if available. If the agent cannot control
Joe's laptop browser, tell Joe the exact URL to open.

For Joe on his laptop:

1. Open the live shared HUD:

```text
http://100.87.143.16:8765/?reset_hud=1
```

2. Select `Joe`.
3. Choose whether to run onboarding.
4. Enter the Compound.
5. Confirm the terminal prompt shows `Joe@compound>`.

For Joe's dev HUD:

```text
http://100.87.143.16:8767/?reset_hud=1
```

For Trey:

```text
http://100.87.143.16:8765/?reset_hud=1
http://100.87.143.16:8766/?reset_hud=1
```

If the login says `Joe is already online` or `Trey is already online`, do not
switch identities. Use the existing open browser session, wait for the old
session to disconnect, or ask Trey before restarting a server.

## Coding Rules

- Work in the operator worktree, not the live folder.
- Keep the live app on `8765` running while coding.
- Use dev HUD `8766` for Trey changes and `8767` for Joe changes.
- Prefer `C:\Python313\python.exe` when running tests on the desktop.
- Do not commit ignored runtime state such as `data\board.json`,
  `data\sparks.json`, logs, local process files, or temporary browser artifacts.
- Generated vault mirrors such as `vault\03_SHARED\OPERATIONAL_BOARD.md` and
  `vault\03_SHARED\WORKSPACE_MAP.md` are usually runtime noise. Commit them
  only when the task intentionally changes vault output.
- If files are already dirty, inspect them. Do not overwrite or revert another
  operator's work unless Trey explicitly approves it.

## Git Loop For Operator Work

Use Joe's path and branch for Joe. Use Trey's path and branch for Trey.

```bat
cd /d D:\The_Compound_Worktrees\Joe
git fetch origin
git status --short --branch
git merge --ff-only origin/master
C:\Python313\python.exe -m unittest discover -s tests
```

Then make the focused change.

```bat
C:\Python313\python.exe -m unittest discover -s tests
git status --short
git diff -- <files you changed>
git add <intentional source/docs/test files>
git diff --cached
git commit -m "<clear focused message>"
git push origin joe/workspace
```

For Trey, push to `trey/workspace`.

Do not merge to `master` unless Trey explicitly approves the merge. When a merge
is approved, update `D:\The_Compound`, run tests, restart the live server, and
verify the live HUD in the browser.

## Merge And Conflict Rules

- Fetch before merging.
- Prefer fast-forward from `master` into a worktree before starting new work.
- If conflicts appear, stop and inspect both sides.
- Preserve intentional work from both Trey and Joe.
- Never use `git reset --hard`, `git checkout -- <file>`, or deletion commands
  to solve a conflict unless Trey explicitly approves the exact destructive
  action.
- After resolving conflicts, run the full tests and browser-check the affected
  HUD.

## Server Recovery Commands

If a port is stuck or a dev server needs a clean restart:

```powershell
$pids = Get-NetTCPConnection -LocalPort 8767 -State Listen -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique
foreach ($procId in $pids) { Stop-Process -Id $procId -Force }
Start-ScheduledTask -TaskName TheCompoundJoeDev
Start-Sleep -Seconds 3
Get-NetTCPConnection -LocalPort 8767 -State Listen
```

Change `8767` and `TheCompoundJoeDev` to the matching Trey or live port/task if
needed.

## Hygiene After Every Commit

- Remove test sparks, board cards, or fake radio messages created for testing.
- Stop temporary SSH tunnels or one-off helper processes.
- Leave only intentional code/docs/tests staged or committed.
- Run `git status --short --branch` and report any remaining dirty files.
- Push the branch only after tests and browser checks pass.

## Quick Success Check

Before saying the work is done, verify:

- The right server responds with HTTP `200`.
- The HUD opens in a browser.
- The correct operator can log in.
- The affected feature works in the browser or WebSocket command path.
- Tests pass.
- Git status is clean except for known runtime-generated files that were
  intentionally left uncommitted.
