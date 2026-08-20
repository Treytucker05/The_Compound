# The Compound Ubiquitous Language

## People and places

- **Member**: A trusted person who belongs in The Compound. The initial members are Trey and Joe.
- **Compound Host**: The primary machine that runs the Compound Hub. For version 1, it is the Windows Desktop; it coordinates the Compound but does not run Member workloads by default.
- **Compound Hub**: The lightweight coordination service on the Compound Host that owns membership, session signaling, Canvas state, and persistent Compound metadata.
- **Private-Network Admission**: The Compound’s network entry boundary. A device already approved on the private network can reach the Compound without a separate Compound invite; an ordinary local-network or public device cannot. It is not a Member identity or a grant of project or computer control.
- **Member Selector**: The per-entry choice of Trey or Joe made on an admitted private-network device. It selects the Member context for that session but is a trusted-network convenience, not a cryptographic proof of who is using the device.
- **Execution Host**: An approved Member computer that runs that Member's actual program, terminal, browser session, development server, or local model. Trey and Joe can each have their own Execution Hosts.
- **Compound Connector**: An approved outbound connection from an Execution Host to the Compound Hub. It advertises only intentionally shared projects and sessions and never grants automatic whole-computer access.
- **Drag to Project**: An explicit gesture from a Connector-provided live app card or thumbnail onto a Canvas Board or Projector Window. It creates a Projected App Session without moving the program or running it on the Compound Hub.
- **Lobby**: The shared social room for presence, text chat, push-to-talk radio, and optional shared Game Tables. It is not a filesystem browser or an administrative console.
- **2D Clubhouse**: The Lobby's visual form: an interactive two-dimensional shared room with clearly labelled Member-presence anchors and Game Tables. It is neither a generic panel dashboard nor a full three-dimensional world.
- **Clubhouse Character**: A small, named, customizable two-dimensional arcade character representing a Member's presence in the 2D Clubhouse. It is a social presence cue, not a required navigation mechanism.
- **Presence Status**: A small, truthful, high-level activity label attached to a Clubhouse Character, such as In Lobby, Working, Watching, Playing, Away, or Offline. It never exposes a project name, file, application, prompt, or screen contents by default.
- **Presence Override**: A Member-controlled Away state that temporarily replaces the automatic Presence Status. It never changes the Member's actual access, sharing, or Radio capability.
- **Retro Arcade Direction**: The visual mood for the 2D Clubhouse: deliberate arcade-era cues, playful social energy, and memorable game objects while preserving legible, modern work and status surfaces.
- **Game Table**: A lightweight, native shared game in the Lobby that Members intentionally open and play together. It is not a Projector Window, a remote application stream, or an access path to a Member's files or computer.
- **Game Table Roadmap**: Basketball Shootout is the first Lobby game. Air hockey, pool, and soccer follow after Basketball is validated and do not block the initial Lobby release.
- **Basketball Shootout**: The first selected Lobby Game Table. Version 1 supports HORSE, Timed Shootout, and Cooperative Target modes.
- **Basketball Game Mode**: A selectable rule set for Basketball Shootout. Version 1 includes HORSE, Timed Shootout, and Cooperative Target modes.
- **HORSE Mode**: The default Basketball Shootout mode. One Member selects a shot position on the shared court and takes a shot; after a made shot, the other Member must try the matching marked position under standard HORSE rules.
- **Workstation**: A Member's persistent work surface in The Compound. It presents that Member's registered projects, AI conversation, terminal, attachments, previews, and share controls through approved Execution Hosts.
- **Project Desk**: The default Workstation layout: a Registered Project Root and files panel on the left, the selected real terminal, browser, or LLM tool surface in the center, and Preview and sharing controls alongside it. It does not create a separate prompt-only AI interface.
- **Project Desk Restore**: Per-Member memory of the last selected project and desk arrangement. It restores layout and context on return but never starts a program, model, terminal, or Connector connection by itself.
- **Project Desk Editor**: The Workstation's editable text and code surface. On an explicit save, it writes the selected file only to the project's Registered Project Root on its Project Home Host through the appropriate Connector; it cannot write outside that root.
- **Explicit Save**: A deliberate save action, including the normal keyboard shortcut, that writes a Project Desk Editor buffer to its source file. Unsaved content has a visible dirty state and recoverable local buffer; it never auto-writes source files.
- **Live Source Collaboration**: A Google-Docs-style shared source-file surface where both Members edit one merged buffer in real time and see each other's labelled caret and selection. It has no writer lock; source persistence follows the current Explicit Save policy.
- **Shared Save State**: The common saved-or-dirty state of a live shared source-file buffer. Real-time edits update the merged buffer immediately but do not alter the underlying source file until an Explicit Save occurs.
- **Shared Save**: An Explicit Save of a live shared source-file buffer that either Member may invoke. It records which Member saved and when.
- **Revision Snapshot**: A retained file-level version created for every Shared Save. It is selected for Revision Compare and never directly changes the live shared buffer or source file.
- **Revision Compare**: A side-by-side, line-level comparison of a Revision Snapshot and the current live shared file. It never changes the buffer or source file; Members manually copy the desired changes before an Explicit Save.
- **Diff Summary**: A human-readable count of lines and sections added, removed, and changed between a Revision Snapshot and the current file.
- **Revision Fingerprint**: A SHA-256 fingerprint of the exact saved file bytes in a Revision Snapshot, used to identify and verify that version's contents.
- **Revision History Drawer**: A shared Project Desk panel beside the Files view that lists Revision Snapshots for the currently selected shared source file and opens Revision Compare.
- **Stage**: A shared viewing surface where a Member intentionally presents a file, page, or live demo to the other Member.
- **Computer Session**: A deliberately opened full-machine-control session targeting an approved Execution Host. It is separate from the ordinary Workstation and from the Lobby.

## Project and collaboration terms

- **Registered Project Root**: A folder deliberately enrolled as a project on its Project Home Host. The ordinary Workstation Files view contains only Registered Project Roots; it does not enumerate the entire host filesystem.
- **Project Home Host**: The one named Execution Host for a project. It holds that project's Registered Project Root, receives its source-file saves, and runs that project's native apps, terminals, and local models.
- **Project Home Host Offline State**: The clear unavailable state shown when the Project Home Host Connector cannot be reached. It exposes no cached project file contents and permits no project browsing, editing, source save, or delayed-sync work.
- **Project Owner**: The Member whose Execution Host is a project's Project Home Host. The Project Owner may invite the other Member to share that project.
- **Project Share Invitation**: An explicit request from a Project Owner to the other Member to share one named project. It states the Project Home Host and must be accepted before the project becomes shared.
- **Collaborator Access**: The default access granted after a Project Share Invitation is accepted. It lets both Members browse only that Registered Project Root and participate in Live Source Collaboration, but grants no terminal, browser, local-model, or full-machine control. It lasts until a Project Access End.
- **Project Access End**: An immediate end of Collaborator Access, triggered when the Project Owner revokes access or the collaborator leaves. It removes the collaborator's project capability without deleting source files, Revision Snapshots, or the Project Home Host's project.
- **Access-End Recovery Draft**: A local-only copy of an unsaved merged source buffer preserved for a Member after a Project Access End. It is not a Revision Snapshot, cannot write to or rejoin the project, and can only be manually copied into a new live buffer after access is granted again.
- **Shared Project**: A Registered Project Root that both Members may open, browse, and edit through active Collaborator Access after the recipient accepts a Project Share Invitation. It retains one Project Home Host.
- **Personal Project**: A Registered Project Root visible only to its Project Owner by default. It becomes a Shared Project only through an accepted Project Share Invitation.
- **Preview**: A rendered file or running local web application shown inside a Workstation or on the Stage.
- **Attachment**: A deliberately stored copy of a file added to a Canvas Board or project. It remains available to permitted Members even when its original Execution Host is offline, and it never grants access to the file's containing folder. It does not expire automatically.
- **Attachment Removal**: A manual action that ends an Attachment's shared availability. The uploader may remove their own Attachment, and a Project Owner may remove any Attachment scoped to their project; it never moves or changes the original file.
- **Canvas Board**: The dedicated shared whiteboard for freeform collaboration. It operates in Collaborative Canvas mode and holds native canvas objects and Projector Windows.
- **Projector Window**: A movable, resizable Canvas Board object that presents one deliberately loaded Attachment, Preview, or Projected App Session with an appropriate renderer. Entering edit mode creates a Projector Draft. It does not grant access to the file's containing folder.
- **Projector Renderer**: A type-specific Projector Window capability. The version 1 set edits code, text, and Markdown; views PDFs and images; plays audio and video; and presents live local web demos.
- **Projector Draft**: A separate shared copy created when a Projector Window enters edit mode. It never automatically overwrites the original source file.
- **Projector Drafts Shelf**: The persistent shared collection of Projector Drafts for a Canvas Board, retaining each draft's associated project or source context.

## Live collaboration terms

- **Radio**: Live, Compound-wide push-to-talk voice communication available from the Lobby, Canvas, Workstations, and Projector views. Radio does not record or transcribe audio by default.
- **Radio Floor**: The exclusive right to transmit on Radio. At most one Member holds the Radio Floor at a time; releasing push-to-talk yields it.
- **Radio Busy State**: The visible state shown when a Member presses push-to-talk while the other Member holds the Radio Floor. The attempted transmission stays silent and is not queued or used to interrupt the speaker.
- **LLM Connection**: A configured, approved route from a Workstation to an AI model or model gateway. A connection never exposes its credential or silently shares one Member's project context with the other.
- **Native LLM Surface**: The actual Codex, CLI, local-model, or browser-based AI interface a Member already uses on an Execution Host. The Compound presents it as a selected Desk surface and may share it only through a deliberate Projected App Session; it does not replace it with a new shared chat box.
- **Projected App Session**: A live terminal, browser, or desktop application on an Execution Host deliberately placed in a Projector Window. It follows Controlled Session rules: the current Driver's clicks and keystrokes route to the actual application, while the other Member observes, annotates, and can request a Driver Handoff.
- **Active Projection**: A live streamed Projected App Session or media source currently using shared projection capacity. Version 1 permits either one Shared Projection or one Reciprocal Peer View, but not both at once.
- **Shared Projection**: One live program or media source presented to both Members in the same Projector Window. It uses Controlled Session rules for underlying application input.
- **Peer Projection**: A one-way live view of a Member's local program sent only to the other Member. The source Member continues using the native local app while the recipient can observe and annotate.
- **Reciprocal Peer View**: A paired mode with one Peer Projection in each direction: Trey sees Joe's selected program and Joe sees Trey's selected program. It has no stream loopback to the source owner.
- **Peer Pane**: A dedicated, labelled pane docked beside a Member's Workstation while Reciprocal Peer View is active. It shows the other Member's Peer Projection and its annotations without replacing the source Member's native local app.
- **Peer View Session**: A mutually started sharing state for Reciprocal Peer View. Once both Members explicitly start it, either Member may deliberately drag an eligible local app into the other Member's Peer Pane without a separate recipient approval for each app.
- **Co-Pilot Cursor**: A visible, Member-labelled pointer used to communicate presence and intent on a shared surface. It does not by itself grant control of the host application.
- **Annotation**: A visual mark anchored to a shared screen, Preview, Stage, or Peer Projection that communicates without changing the underlying application. In a Peer Projection, the source Connector renders the remote Member's Annotation over the source Member's local app. An Annotation expires when its session ends unless a Member explicitly saves it.
- **Collaborative Canvas**: A shared surface that permits Members to manipulate independent canvas objects concurrently.
- **Controlled Session**: A shared program or test surface that permits exactly one Driver to alter the underlying application at a time.
- **Driver**: The Member currently entitled to send host input during a Controlled Session.
- **Driver Handoff**: A request by a non-Driver to take host input in a Controlled Session. The current Driver approves or releases it; no Member silently takes control.
- **Primary Editor**: The first Member to focus a canvas text object during a concurrent edit. The Primary Editor receives deterministic ordering priority for a collision, without discarding the other Member's text.

## Core boundaries

- The Lobby is shared by design; Workstations and projects are explicit collaboration surfaces.
- The Compound Hub coordinates Members and shared state; a project workload runs on its originating Execution Host by default.
- Everyday file navigation begins with Registered Project Roots.
- Full-machine control is deliberate and distinct from normal project work.
- Sharing to the Stage changes what the other Member can view, not who owns a project or its files.
