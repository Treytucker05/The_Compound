# The Compound V1 — Shared Studio Product Plan

> **Status:** Review draft for Trey and Joe. No product implementation begins until both have reviewed this plan through a Grill Me session.

> **Decision source:** [`CONTEXT.md`](../../../CONTEXT.md) and ADRs `0001` through `0045` on branch `trey/compound-shared-studio-program`. The ADRs are the authority when this plan summarizes a decision.

## Product promise

The Compound is one place where Trey and Joe can hang out, talk, play light games, and do real work together without moving either person's programs, models, or entire computer onto the Windows Desktop. The social experience and the work experience are designed as connected rooms in the same product, not as a chat app bolted onto remote desktop software.

## Shape of the product

```text
                 Private network only
                         │
                  Compound Hub
     membership · signaling · Canvas state · metadata
                         │
          ┌──────────────┴──────────────┐
          │                             │
     Trey's Execution Host          Joe's Execution Host
    projects · apps · LLMs         projects · apps · LLMs
          │                             │
          └──── intentional Connectors ─┘
                         │
       Lobby ───── Canvas Board ───── Project Desks
        radio          projector           real work
```

The Windows Desktop is the lightweight coordination host. It does not become the default place to run heavy project apps, terminals, development servers, or local models.

## What is already decided

### Social space

- The Lobby is a 2D retro-arcade Clubhouse with named, customizable Trey and Joe characters.
- Presence is a high-level, automatic status with an Away override; it never reveals private project, prompt, file, or screen details.
- Radio is push-to-talk across Lobby, Canvas, Workstations, and Projectors. One Member holds the Radio Floor; a second press is visibly busy and silent, never queued or interrupting.
- Basketball Shootout launches first with HORSE as the default, plus Timed Shootout and Cooperative Target. Air hockey, pool, and soccer follow later.

### Canvas and Projectors

- **Canvas is part of the first working slice.** It is the shared whiteboard and the common place to arrange Projector Windows, not a later add-on.
- Both Members can manipulate independent Canvas objects at the same time. For a shared text object, both people see live text and labelled carets; first focus has deterministic collision ordering without a writer lock.
- A Projector Window is movable and resizable. It can edit text, code, and Markdown through a separate Projector Draft; view PDFs and images; play audio and video; and present live local web demos.
- A standalone file added to Canvas or a project becomes a deliberate Attachment copy. It remains available when the source computer disconnects, never exposes the containing folder, and stays until manually removed.

### Project Desks and files

- Each Workstation opens as a Project Desk: files on the left, a selected real tool surface in the center, and preview/share controls beside it. It restores the last selected project and layout without starting anything automatically.
- Every project has one Project Home Host. That computer holds the real registered project folder, accepts source-file saves, and runs the native app, terminal, server, and local model for that project.
- Sharing a project is explicit: its owner sends an invitation and the other Member accepts. Acceptance gives Collaborator Access to that registered project root and live source editing, not to the rest of the computer.
- Shared source files use one Google-Docs-style live buffer with both carets visible. Either Member may explicitly save. An explicit save writes only to the Project Home Host and creates a retained file-level Revision Snapshot.
- Revision history lives in a shared drawer beside Files. Comparing a revision is side-by-side and manual: it shows a readable diff summary and SHA-256 fingerprint, then a Member manually copies desired content into the live buffer before saving.
- If project access ends, unsaved content is preserved only as a local recovery draft. It cannot save, sync, or rejoin the project unless access is granted again.
- If the Project Home Host is offline, the project is clearly unavailable: no cache browsing, offline edits, source saves, delayed sync, app, terminal, or model session.

### Real apps, models, and computer control

- A Native LLM Surface is the real Codex, CLI, browser, or local-model UI a Member already uses. The Compound never replaces it with a new generic shared chat box.
- Drag to Project is the way to intentionally place a live app into a Projector Window. The source app stays on its Execution Host.
- A Shared Projection shows one live app to both Members. A mutually started Reciprocal Peer View is the bounded alternative for parallel work: each person sees the other's selected app in a dedicated peer pane without a stream loopback.
- A normal projection or full-computer session has one Driver. The co-pilot can observe, annotate, and request a handoff; there is no literal second remote mouse controlling the host OS.
- A whole Computer Session is separate from project sharing and requires the target computer owner's approval every time.

### Trust boundary

- The Compound is reachable only from approved private-network devices, not the public internet or ordinary local Wi-Fi by itself.
- An admitted device chooses Trey or Joe on each entry. This is intentionally fast but is an asserted identity, not strong proof of the person using the device.
- Private-network admission, project sharing, and a previous session never create blanket full-computer access.

## V1 build sequence

### Milestone 0 — Trey and Joe review gate

- [ ] Trey reads this plan, `CONTEXT.md`, and the linked ADRs.
- [ ] Joe runs a Grill Me review using the prompt in [`COMPOUND_V1_REVIEW.md`](../../../vault/03_SHARED/COMPOUND_V1_REVIEW.md).
- [ ] Any accepted change is recorded as a new ADR or glossary correction on the planning branch.
- [ ] Trey and Joe both mark the plan accepted before implementation work is opened.

### Milestone 1 — Shared Work Surface

This is the first working slice. It intentionally includes the **Canvas** and the **Project Desk** together.

- [ ] Private-network entry and the Trey/Joe Member Selector.
- [ ] Canvas Board with persistent objects, live cursors, annotations, and movable/resizable Projector Windows.
- [ ] Project Desk shell with registered project list, project-home-host label, clear offline state, and deliberate project-share invitations.
- [ ] Attachment copy upload, durable availability, file-type renderers, and manual removal controls.

**Acceptance scenario:** Trey and Joe enter from approved devices, meet on one Canvas, attach a PDF or video, move and annotate it together, open an accepted shared project, and see exactly which computer owns the real project files.

### Milestone 2 — Live Source Collaboration and Revision Safety

- [ ] Google-Docs-style merged source buffers with labelled carets and selections.
- [ ] Explicit Shared Save from either Member to the Project Home Host.
- [ ] Dirty state, recoverable local buffer, retained Revision Snapshots, history drawer, diff summary, SHA-256 fingerprint, and manual compare/copy workflow.
- [ ] Access-end, recovery-draft, revoke, leave, and offline-host states.

**Acceptance scenario:** Trey and Joe edit one source file live, either saves it, inspect the exact saved revision, manually recover a prior change, and see no accidental write when a share ends or the home host disappears.

### Milestone 3 — Connectors, Native Tools, and Projected Apps

- [ ] Per-host Connector that advertises only approved projects and intentionally shareable native surfaces.
- [ ] Real terminal, browser, Codex, and local-model surfaces inside a Project Desk without transferring credentials to the Hub.
- [ ] Drag to Project, one Shared Projection, mutually started Reciprocal Peer View, annotations, and Driver Handoff.
- [ ] Capacity enforcement: one shared heavy projection or one reciprocal peer-view pair, never an uncontrolled pile of heavy streams on the Windows Desktop.

**Acceptance scenario:** Trey keeps a heavy app running on his laptop, drags it into a Projector, Joe sees and annotates it, and they hand control over cleanly without moving the app or model to the Hub.

### Milestone 4 — Clubhouse and Radio

- [ ] 2D retro-arcade Lobby, named characters, automatic presence, Away override, and text chat.
- [ ] Compound-wide Radio control with a clearly shown floor holder and busy state.
- [ ] Visual accessibility review: status must not depend on color alone, and work surfaces remain clear rather than arcade-themed dashboards.

**Acceptance scenario:** While working from Project Desks or Canvas, Trey and Joe can push-to-talk across surfaces, see each other's truthful high-level status, and return to the Clubhouse without losing work context.

### Milestone 5 — Lobby Games

- [ ] Basketball Shootout with HORSE, Timed Shootout, and Cooperative Target.
- [ ] Validate Basketball as a lightweight native Lobby Game Table before air hockey, pool, or soccer.
- [ ] Add the remaining games only after the shared state, input model, and performance are proven.

### Milestone 6 — Deliberate Whole-Computer Sessions

- [ ] Request and owner-approval flow that names the target Execution Host.
- [ ] One-Driver full-computer control, co-pilot annotation, visible handoff, clean end state, and no reconnect grant.
- [ ] Keep this separate from ordinary Project Desk and Projector use.

## Non-negotiable boundaries

- The Hub coordinates; an Execution Host runs a Member's real workload.
- A Connector shares only what its owner intentionally advertises. It is not filesystem or whole-computer access.
- A shared project is one home folder on one home computer, not an automatic multi-computer mirror.
- Real source writes are explicit, scoped to a registered root, and revisioned. Projector edits are separate drafts until deliberately copied or saved.
- A view, annotation, project invitation, private-network connection, or prior session never by itself grants application input or full-computer control.
- No production data migration, service restart, deployment, credentials change, or model-default change is part of this review plan.

## Implementation decisions intentionally deferred until after review

- Exact Canvas realtime/CRDT implementation and persistence format.
- Exact Connector capture, video encoding, stream transport, and performance telemetry.
- Attachment storage provider, encryption-at-rest details, quota policy, and backup design.
- Exact private-network product and any later device-pairing or passkey upgrade.
- Exact model-provider adapters and Connector packaging.

These are implementation choices, not product behavior changes. They must be selected against the actual codebase and verified environment after Trey and Joe accept the product plan.

## Review completion standard

The review is complete only when both Trey and Joe agree that the plan preserves the desired social hangout, Canvas collaboration, real local work tools, and safety boundaries. A finished review produces one of these outcomes:

- **Accepted:** begin implementation from Milestone 1.
- **Accepted with ADR changes:** update the planning branch, then accept the revised plan.
- **Needs redesign:** record the disagreement and return to one-question-at-a-time grilling before code changes.
