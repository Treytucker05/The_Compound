# Trey Handoff Checklist

## Prep Once Before Invite
1. Confirm launcher entrypoint exists:
   - `C:\COMPOUND_APPROACH\start_portal.bat`
2. Confirm key docs exist:
   - `C:\COMPOUND_APPROACH\vault\04_SYSTEM\TREY_ONBOARDING.md`
   - `C:\COMPOUND_APPROACH\vault\03_SHARED\PORTAL_MISSIONS.md`
   - `C:\COMPOUND_APPROACH\vault\03_SHARED\OPERATIONAL_BOARD.md`
   - `C:\COMPOUND_APPROACH\vault\03_SHARED\DECISION_LOG.md`
3. If needed, run setup:

```powershell
cd C:\COMPOUND_APPROACH
scripts\setup.bat
```

## Launch Expectation
- Trey runs `start_portal.bat`
- Launcher auto-launches engine + HUD + vault
- Interactive onboarding appears in HUD

## Safety Checks
- Auto-launch is enabled by default.
- If guide does not appear, click **Guide Me** in HUD.
- If portal does not start:

```powershell
cd C:\COMPOUND_APPROACH
scripts\setup.bat
start_portal.bat
```
