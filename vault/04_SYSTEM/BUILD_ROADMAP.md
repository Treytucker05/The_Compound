# COMPOUND_APPROACH Build Roadmap

## Executive Summary

**Project:** Text-based MUD with AI-powered NPCs grounded in a truth hierarchy that prevents hallucination drift.

**Core Innovation:** Neo4j graph database enforcing Canon > Observed > Hypothesis truth levels with mandatory evidence relationships.

**Status:** MUD server runs. Launcher built. Vault ready. Neo4j integration files **planned**, not yet implemented.

---

## What Exists (Verified)

| Component | File(s) | Status |
|-----------|---------|--------|
| WebSocket MUD Server | `engine/server.py` | ✅ Running |
| Filesystem World Engine | `engine/world.py` | ✅ Active |
| Kanban Board | `engine/board.py` | ✅ Active |
| Python Launcher | `launcher/` | ✅ Active |
| Obsidian Vault | `vault/` | ✅ Active |
| AI Backend Seam | `engine/ai_stub.py` | ✅ Stub only |

## What's Planned (Not Yet Built)

| Component | Purpose |
|-----------|---------|
| `create_schema.cypher` | Neo4j schema with constraints/indexes |
| `neo4j_driver.py` | Connection wrapper + query helpers |
| `validate_fact.py` | Policy enforcement before writes |
| `ingest_canon.py` | Bible/policy chunking pipeline |
| `bruce_agent.py` | LangGraph agent with tools |
| `distillation_cron.py` | Event → Fact extraction scheduler |

---

## Architecture (Target)

```
┌─────────────────────────────────────────────────────────────┐
│                     PLAYER (Browser)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  COMPOUND_APPROACH Engine                    │
│  engine/server.py                                           │
│  - Command parser                                            │
│  - Room/NPC/Item management                                  │
│  - Player sessions                                           │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│     Bruce Agent         │     │      Neo4j Driver           │
│  bruce_agent.py         │     │   neo4j_driver.py           │
│  - LangGraph workflow   │◄───►│   - Query helpers           │
│  - Tool: search_canon   │     │   - create_fact()           │
│  - Tool: log_observation│     │   - log_event()             │
│  - Ollama LLM calls     │     │   - get_*_facts()           │
└─────────────────────────┘     └─────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Neo4j Graph                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │ :Source │───►│ :Chunk  │◄───│ :Fact   │                  │
│  │ (Canon) │    │ (verses)│    │ (truth) │                  │
│  └─────────┘    └─────────┘    └────┬────┘                  │
│                                      │                       │
│                                      ▼                       │
│                               ┌─────────┐                    │
│                               │ :Event  │                    │
│                               │ (logs)  │                    │
│                               └─────────┘                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Distillation Cron                               │
│  distillation_cron.py                                        │
│  - Micro: every 15 min (recent observations)                │
│  - Nightly: preferences + hypotheses                        │
│  - Weekly: pattern detection, conflict flags                │
└─────────────────────────────────────────────────────────────┘
```

---

## Truth Hierarchy (Non-Negotiable)

```
CANON (highest authority)
  │  Source: Bible, policies, approved lore
  │  Relationship: [:CITES]->(:Chunk)
  │  Rule: Exact quotes only, never paraphrase
  │
  ▼
OBSERVED (direct evidence)
  │  Source: Events the system witnessed
  │  Relationship: [:EVIDENCED_BY]->(:Event)
  │  Rule: Must link to logged events
  │
  ▼
HYPOTHESIS (inference, uncertain)
     Source: Pattern detection, guesses
     Relationship: [:EVIDENCED_BY]->(:Event) + expires_at
     Rule: Auto-expires, labeled "Hypothesis" in output
```

---

## Build Order (Prioritized)

### Phase 1: Neo4j Foundation ⏱️ 2 hours
1. Install Neo4j Desktop or connect to Aura
2. Run `create_schema.cypher` to initialize constraints
3. Test connection with `neo4j_driver.py`

### Phase 2: Canon Ingestion ⏱️ 1 hour
1. Ingest approved Canon sources via `ingest_canon.py`
2. Verify chunks in Neo4j Browser

### Phase 3: Wire Bruce Agent ⏱️ 2 hours
1. Replace mock AI with `bruce_agent.py`
2. Test responses for truth compliance

### Phase 4: Start Distillation ⏱️ 30 min
1. Run `distillation_cron.py` manually
2. Schedule as background task

### Phase 5: Integration Test ⏱️ 1 hour
1. Start engine
2. Talk to Bruce, verify he cites Canon
3. Check Neo4j for logged events

---

## Next Session Handoff

**For any AI continuing this work:**

1. All active code is in `c:\COMPOUND_APPROACH\engine\` and `c:\COMPOUND_APPROACH\launcher\`
2. Neo4j schema is designed, not yet deployed
3. Bruce agent is specced, needs implementation
4. User prefers local LLMs (Ollama) over cloud where possible
5. First task for next session: pick a Phase and execute it

---

*Document compiled May 2026*
*COMPOUND_APPROACH v1.0*
