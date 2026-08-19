# The Compound Ubiquitous Language

## People and places

- **Member**: A trusted person who belongs in The Compound. The initial members are Trey and Joe.
- **Compound Host**: The primary machine that owns persistent Workstations and Computer Sessions. For version 1, the Compound Host is the Windows Desktop.
- **Lobby**: The shared social room for presence, text chat, push-to-talk radio, and optional games. It is not a filesystem browser or an administrative console.
- **Workstation**: A Member's persistent work surface in The Compound. It presents that Member's registered projects, AI conversation, terminal, attachments, previews, and share controls.
- **Stage**: A shared viewing surface where a Member intentionally presents a file, page, or live demo to the other Member.
- **Computer Session**: A deliberately opened full-machine-control session. It is separate from the ordinary Workstation and from the Lobby.

## Project and collaboration terms

- **Registered Project Root**: A host folder deliberately enrolled as a project. The ordinary Workstation Files view contains only Registered Project Roots; it does not enumerate the entire host filesystem.
- **Shared Project**: A Registered Project Root that both Members may open from their Workstations.
- **Personal Project**: A Registered Project Root normally visible to one Member that can be deliberately presented or shared.
- **Preview**: A rendered file or running local web application shown inside a Workstation or on the Stage.
- **Attachment**: A file deliberately added to a conversation, project, or Stage. An attachment is not an implicit grant to browse its containing folder.
- **Canvas Board**: The dedicated shared whiteboard for freeform collaboration. It operates in Collaborative Canvas mode and holds native canvas objects and Projector Windows.
- **Projector Window**: A movable, resizable Canvas Board object that presents one deliberately loaded Attachment or Preview with an appropriate reader, editor, or media player. Entering edit mode creates a Projector Draft. It does not grant access to the file's containing folder.
- **Projector Draft**: A separate shared copy created when a Projector Window enters edit mode. It never automatically overwrites the original source file.

## Live collaboration terms

- **Radio**: Live, push-to-talk voice communication in The Compound. Radio does not record or transcribe audio by default.
- **Radio Floor**: The exclusive right to transmit on Radio. At most one Member holds the Radio Floor at a time; releasing push-to-talk yields it.
- **LLM Connection**: A configured, approved route from a Workstation to an AI model or model gateway. A connection never exposes its credential or silently shares one Member's project context with the other.
- **Co-Pilot Cursor**: A visible, Member-labelled pointer used to communicate presence and intent on a shared surface. It does not by itself grant control of the host application.
- **Annotation**: A visual mark anchored to a shared screen, Preview, or Stage that communicates without changing the underlying application. An Annotation expires when its session ends unless a Member explicitly saves it.
- **Collaborative Canvas**: A shared surface that permits Members to manipulate independent canvas objects concurrently.
- **Controlled Session**: A shared program or test surface that permits exactly one Driver to alter the underlying application at a time.
- **Driver**: The Member currently entitled to send host input during a Controlled Session.
- **Driver Handoff**: A request by a non-Driver to take host input in a Controlled Session. The current Driver approves or releases it; no Member silently takes control.
- **Primary Editor**: The first Member to focus a canvas text object during a concurrent edit. The Primary Editor receives deterministic ordering priority for a collision, without discarding the other Member's text.

## Core boundaries

- The Lobby is shared by design; Workstations and projects are explicit collaboration surfaces.
- Everyday file navigation begins with Registered Project Roots.
- Full-machine control is deliberate and distinct from normal project work.
- Sharing to the Stage changes what the other Member can view, not who owns a project or its files.
