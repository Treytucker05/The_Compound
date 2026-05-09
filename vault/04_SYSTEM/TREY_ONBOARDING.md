# Trey Onboarding (5 Minutes)

## Goal
Start the portal, open the HUD + vault, and complete one real task.

## First Time Setup (once)
1. Open `C:\COMPOUND_APPROACH`.
2. Run `scripts\setup.bat`.
3. Wait for setup to finish.

## Daily Start
1. Double-click `start_portal.bat`.
2. In launcher, choose profile: **Trey**.
3. Wait for auto-launch (engine + HUD + vault start automatically).
4. Wait for:
   - Web HUD to open (`http://localhost:8765`)
   - Obsidian vault to open
5. Follow the in-app **Interactive Onboarding** overlay in the HUD.

## First Session Workflow
1. In HUD terminal (left pane), enter your name.
2. Run:
   - `board`
   - `add <one concrete task>`
   - `working on <that task>`
3. Do the work.
4. Log completion:
   - `done <task> -- <result>`

## Where To Look
- Shared mission context: `vault/03_SHARED/PORTAL_MISSIONS.md`
- Shared board mirror: `vault/03_SHARED/OPERATIONAL_BOARD.md`
- Daily capture template: `vault/00_DAILY/QUICKSTART_TODAY.md`

## If Something Breaks
1. In launcher, click **Stop Engine**.
2. Close launcher.
3. Re-open `start_portal.bat`.
4. Click **Launch Portal** again.

If it still fails, check launcher log panel for preflight errors.
