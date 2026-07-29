---
name: persona-flow-audit
description: >
  Persona operations map and spec audit skill (part of the ATDD toolkit). Use
  this skill when the user wants to audit BDD/acceptance specs by persona, map
  critical flows per role, identify which operations each persona performs and
  in what order, find coverage gaps, detect wrong persona tags, or produce a
  persona operations map document. Triggers include: "persona map", "operations
  map", "critical flows", "persona audit", "who does what", "spec audit by
  persona", "role mapping", "flow mapping", "persona flow audit", or any request
  to understand what each user role does in the system through the lens of BDD
  specs. Always use this skill for these tasks.
---

# Persona Flow Audit: Persona Operations Map

## Prerequisites

This skill depends on BDD conventions from the sibling `acceptance-spec-authoring`
skill. Before starting, read the BDD manifesto to understand tagging taxonomy
(especially Dimension 5: Persona) and naming conventions:

```
../acceptance-spec-authoring/references/bdd-manifesto.md
```

Read only the **Tagging Taxonomy**, **Naming Conventions**, and **Repository
Structure** sections. You do not need the full process flows for this audit.

---

## When to Use

| User intent | This skill? |
|---|---|
| Map what each persona does in the system | Yes |
| Audit specs grouped by role/persona | Yes |
| Find missing scenarios per persona | Yes |
| Identify wrong persona tags | Yes |
| Produce a persona operations document | Yes |
| Review specs for general gaps/duplicates | No — use BDD Process 5 (Spec Audit) |
| Write new specs from a requirement | No — use BDD Process 1 |

---

## Required Inputs

- Full `/specs/` directory access (all `.feature` files)
- Application code access (routes, controllers, components, middleware, RBAC/permissions)
- Product feature list or changelog (optional, helps identify unlisted features)

---

## Process

### Phase 1 — Spec Extraction

Read all `.feature` files under `/specs/features/` and `/specs/bugs/`.

For each scenario, extract:
- Scenario ID (`@F-NNN-S-NN`)
- Persona tags (`@persona:<name>`)
- Feature title (from `Feature:` line)
- Scenario title (from `Scenario:` line)
- Steps summary (Given/When/Then — just the action verbs, not full text)

Build a **scenario registry** — a flat list of all scenarios with their metadata.
This is your working dataset for the rest of the audit.

If a scenario has no `@persona:` tag, infer it from the Feature's "As a ..." line.
If neither exists, flag it as `@persona:unknown`.

### Phase 2 — Code Review

Understand the application architecture to inform flow construction:

1. **Entry points:** Scan routes, navigation, sidebar menus, dashboards — what screens exist?
2. **RBAC mapping:** Check permission checks, role guards, middleware — which personas can access what?
3. **Dependency chains:** Identify what must exist before what (e.g., "product must exist before BOM can be created")
4. **Unspecced features:** Note any features visible in code but absent from the scenario registry

Do not spend excessive time on code review. The goal is to understand the
application well enough to construct meaningful flows, not to audit the codebase.

### Phase 3 — Flow Construction

For each persona identified in Phase 1:

1. **Group scenarios by operational purpose** — not by feature area. A "Daily Operations" flow may span 5 feature areas.
2. **Name each flow** by what the persona is trying to accomplish (e.g., "Initial System Setup", "Daily Submission", "Schedule Communication")
3. **Order operations within each flow** by dependency or temporal sequence. Each row in the flow table is one operation that may reference 1-N scenarios.
4. **Label each flow's cadence:**
   - `one-time` — run once per environment (e.g., initial setup)
   - `daily` — every working day or shift
   - `periodic` — weekly, monthly, quarterly
   - `on-demand` — triggered by events (e.g., bug report, export request)
   - `edge-case` — resilience, error handling, offline scenarios
5. **Flag operations with no scenario** — these are gaps to report in Phase 4

**Flow construction heuristics:**
- Start with the persona's primary goal (the "As a ..." line from their Feature descriptions)
- Group by what the persona SEES (screens/pages), what they DO (CRUD, workflows), and what they MONITOR (dashboards, alerts)
- If a persona has >5 flows, consider whether some are sub-flows that should be nested

### Phase 4 — Gap Analysis

Produce four categories of findings:

1. **Wrong persona tags:** Scenarios tagged with persona X but the action described is performed by persona Y. Evidence: the action requires permissions that persona X does not have, or the Feature description contradicts the tag.

2. **Missing scenarios:** Operations that exist in code (Phase 2) or are implied by existing scenarios but have no spec coverage. For each gap, provide:
   - Why it's missing (what evidence suggests this operation should exist)
   - A suggested scenario title (not full Gherkin — just `Scenario: [title]`)

3. **Orphaned / ambiguous personas:** Persona tags that overlap, are too generic, or represent the same real person at different lifecycle stages without clear boundaries.

4. **Unassigned scenarios:** Scenarios from the registry that could not be placed in any persona's flow. These may indicate a missing persona or a misclassified scenario.

---

## Output Format

Output file: `/specs/audits/persona-operations-map-[date].md`

Reference the template:

```
/references/output-template.md
```

**Key format rules:**
- Flow tables use only 3 columns: `#`, `Critical Operation`, `Scenario IDs` — no feature file column. The scenario ID is the canonical reference; the file can be located via `_index.json`.
- Personas are numbered in the operations map (2.1, 2.2, ...) ordered by operational importance (most scenarios / most critical flows first).
- Flows within a persona are numbered and named by purpose, not by feature area.
- Gaps are grouped by persona, not by gap type.
- "Recommended Next Steps" are prioritized by operational impact: immediate (tag fixes) > high (missing critical flows) > medium > low (design discussions).

---

## Rules

- **Read-only audit.** Do not modify any `.feature` file. Report only.
- **Every scenario must appear exactly once** in the operations map. If a scenario fits multiple flows, assign it to the primary flow and note the cross-reference.
- **After human confirms findings:** gap scenarios are created via BDD Process 1 (New Feature Request), persona tag fixes are applied as spec edits.
- **Do not invent personas.** Only report personas found in `@persona:` tags or Feature "As a ..." lines. If a persona is implied by code but never tagged, report it as a finding, not as an established persona.
- **Dependency ordering is critical.** If a flow has dependency chains (step 2 requires step 1), mark it with the note: "Execute in this order. Each step unblocks the next."

---

## What You Must Never Do

- Modify any `.feature` file during the audit
- Create new scenarios without human approval (suggest them in the gaps section)
- Assign a scenario to multiple flows (pick one, cross-reference the other)
- Omit a scenario from the map — every scenario in the registry must appear somewhere
- Include feature file names in flow tables (use scenario IDs only)
