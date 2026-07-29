# Persona Operations Map — Output Template

Use this template when producing the audit output. Replace all `[placeholders]`
with actual values. Remove sections that have no findings (e.g., if there are no
orphaned personas, omit section 4.3).

---

```markdown
# [Project Name] — Persona Operations Map
**Date:** [YYYY-MM-DD]
**Process:** BDD Spec Audit — Persona Operations Map
**Scope:** All [N] `.feature` files in `specs/features/`
**Method:** Full persona extraction, critical flow mapping, scenario assignment, gap analysis

---

## 1. Personas Identified

| Persona Tag | Description | Primary Role |
|---|---|---|
| `@persona:[name]` | [extracted from Feature "As a ..." lines] | [one-line role summary] |

---

## 2. Persona Operations Map

### 2.1 [Persona Display Name] (`@persona:[name]`)

**Primary goal:** [one sentence — what this persona's main objective is in the system]

#### Flow 1 — [Flow Name] ([cadence])
> [If dependency-ordered: "Execute in this order. Each step unblocks the next."]

| # | Critical Operation | Scenario IDs |
|---|---|---|
| 1 | [operation description] | [F-NNN-S-NN, F-NNN-S-NN] |
| 2 | [operation description] | [F-NNN-S-NN] |

#### Flow 2 — [Flow Name] ([cadence])

| # | Critical Operation | Scenario IDs |
|---|---|---|
| 1 | [operation description] | [F-NNN-S-NN] |

[Repeat flows for this persona, then repeat persona sections (2.2, 2.3, ...)]

---

## 3. Coverage Summary

| Persona | Scenarios | Critical Flows |
|---|---|---|
| `@persona:[name]` | ~[N] | [N] flows covered |
| **TOTAL** | **~[N]** | |

---

## 4. Gaps and Missing Scenarios

### 4.1 Wrong Persona Tagging

| Scenario IDs | Current Tag | Should Be | Reason |
|---|---|---|---|
| [F-NNN-S-NN, ...] | `@persona:[x]` | `@persona:[y]` | [why the current tag is wrong] |

### 4.2 Missing Scenarios — [Persona Name]

| Gap | Description | Suggested Scenario |
|---|---|---|
| **[short label]** | [why this is missing and what evidence suggests it should exist] | `Scenario: [suggested title]` |

[Repeat 4.2 for each persona that has gaps]

### 4.3 Orphaned / Ambiguous Personas

| Persona | Issue |
|---|---|
| `@persona:[name]` | [description of overlap, ambiguity, or missing boundary definition] |

### 4.4 Unassigned Scenarios

| Scenario ID | Title | Issue |
|---|---|---|
| [F-NNN-S-NN] | [scenario title] | [why it couldn't be placed in any flow] |

---

## 5. Scenario Count by Feature Area

| Feature Area | Scenarios | Persona(s) |
|---|---|---|
| [area name] | [N] | [comma-separated persona list] |
| **TOTAL** | **[N]** | |

---

## 6. Recommended Next Steps

### Immediate (tagging fixes — no new specs)
1. [specific fix with scenario IDs]

### High Priority (missing critical flows)
2. [specific gap with operational impact]

### Medium Priority
3. [gap or improvement]

### Low Priority / Design Discussion
4. [persona consolidation, boundary clarification, etc.]
```

---

## Template Notes

- **Section 4 subsections are optional.** Omit any subsection with no findings
  (e.g., if all personas are clean, omit 4.3).
- **Section 2 persona ordering:** Most operationally important persona first
  (typically the one with the most scenarios or the most critical flows).
- **Flow cadence values:** `one-time`, `daily`, `periodic`, `on-demand`, `edge-case`.
- **Scenario IDs in tables:** Comma-separated on a single line. If more than 6 IDs
  for one operation, use range notation: `F-NNN-S-01..F-NNN-S-06`.
- **Gap descriptions:** Always explain WHY the gap matters (operational impact),
  not just WHAT is missing.
