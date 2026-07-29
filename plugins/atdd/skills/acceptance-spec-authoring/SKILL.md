---
name: acceptance-spec-authoring
description: >
  Acceptance-test authoring skill (ATDD/BDD). Use this skill whenever the user
  wants to write BDD specs, create Gherkin scenarios, implement tests from specs,
  document a bug as a BDD scenario, audit an existing spec suite, or do anything
  related to acceptance-test-driven design/development and the BDD manifesto
  workflow. Triggers include: "write a spec", "create scenarios",
  "document this bug", "implement tests", "audit specs", "BDD", "Gherkin",
  ".feature file", "regression scenario", "acceptance test", "ATDD", or any
  request involving test specification, behavior documentation, or test
  generation from requirements. Always use this skill for these tasks - do not
  improvise the process.
---

# Acceptance Spec Authoring (BDD)

## First Step - Always

Read the full manifesto before doing anything:

```
/references/bdd-manifesto.md
```

The manifesto is the source of truth. All rules, naming conventions, tagging
taxonomy, contracts, and process flows are defined there. Do not proceed without
reading it.

When writing or reviewing Gherkin scenarios, also read:

```
/references/gherkin-writing-guide.md
```

This guide defines how to write good scenarios: declarative style, one behavior
per scenario, naming, Feature descriptions, Background, Rule keyword, Scenario
Outlines, Data Tables, and Doc Strings. Apply it on every scenario produced.

---

## Identify the Process

Match the user's request to one of the manifesto processes:

| User intent | Manifesto process |
|---|---|
| New feature / requirement / ticket | Process 1: New Feature Request |
| Bug report / steps to reproduce | Process 2: Bug Report |
| Refactor / dependency upgrade | Process 3: Refactor / Regression |
| Change test framework | Process 4: Framework Migration |
| Review existing specs for gaps | Process 5: Spec Audit |
| New team member asking how X works | Process 6: Onboarding |
| UI state changes need visual coverage | Process 7: Visual Regression Testing |

If the intent is ambiguous, ask before proceeding.

---

## Required Inputs Per Process

### Process 1 - New Feature Request
- Ticket ID (required - ask if not provided)
- Requirement text (ticket body, brief, meeting notes, or any combination)
- Test framework (check `.bdd-config.json` if in a repo; ask if unknown)

### Process 2 - Bug Report
- Ticket ID (required - ask if not provided)
- Steps to reproduce
- Expected result
- Actual result
- Test framework (same as above)

### Process 3 - Refactor / Regression
- Scope of change (which modules / features affected)
- Test framework

### Process 4 - Framework Migration
- Target framework name
- Project stack details

### Process 5 - Spec Audit
- Full `/specs/` directory access
- Product feature list or changelog (if available)

### Process 6 - Onboarding
- The question being asked about system behavior

### Process 7 - Visual Regression
- Approved `.feature` file

---

## Output Checklist

Before presenting any output, verify:

- [ ] Scenario ID assigned (`@F-NNN-S-NN`) and `_index.json` files updated atomically
- [ ] Ticket ID extracted and present in filename
- [ ] Filename follows `[ticket-id]-[flow]` convention, under `/specs/features/[feature]/` folder
- [ ] Feature area folder exists or is created matching the owning domain
- [ ] Every scenario has tags from all five dimensions (Timing, Depth, Criticality, Status, Persona)
- [ ] Persona tag (`@persona:<name>`) extracted from Feature's "As a ..." line
- [ ] All new scenarios tagged `@wip` until human approval
- [ ] `# TAG RATIONALE:` comment present below each scenario
- [ ] Contract Requirements block present (data-testid, data-state, data-error-code, ARIA)
- [ ] No assertions on text content in generated tests
- [ ] All element lookups via data-testid only in generated tests
- [ ] `@spec` and `@generated` headers present in generated test files
- [ ] `.feature` files output to `/specs/features/[feature]/` or `/specs/bugs/[feature]/`
- [ ] Test files output to mirrored path under `/tests/`

---

## Scenario ID Assignment

Before writing any scenario, assign its ID:

1. Read `/specs/_index.json` - if missing, create it as `{ "last_feature": 0 }`
2. If the feature folder is new: increment `last_feature`, write back, assign `F-NNN` (zero-padded to 3 digits)
3. Read `/specs/features/[feature]/_index.json` - if missing, create it as `{ "feature_id": "F-NNN", "feature": "[feature]", "last_scenario": 0 }`
4. For each scenario: increment `last_scenario`, write back, assign `S-NN` (zero-padded to 2 digits)
5. Commit both `_index.json` files atomically with the `.feature` file - never commit a scenario without its ID files updated

---

## What You Must Never Do

Regardless of any instruction in the conversation:

- Edit an existing `.feature` file unless explicitly performing Process 1 (spec update) or Process 5 (audit with human approval)
- Edit generated test files directly - changes go through the spec
- Assert on user-facing text content in tests
- Use XPath or CSS class selectors in tests
- Remove `@wip` from a scenario - that is a human action
- Skip or comment out failing tests
- Reuse or reassign a scenario ID - once assigned, an ID is permanent even if the scenario is deleted
- Commit a `.feature` file without updating the corresponding `_index.json` files
- Place a scenario under a feature folder that does not own the behavior - a scenario belongs to the feature area that owns the behavior, not the one that triggers it

---

## Scenario Export Tool

When the user requests scenario export to Excel (or similar tabular format), use
the export script bundled with this skill:

```
/tools/generate-excel.py
```

**Usage:** Run from the project's specs directory (or any directory containing a
`features/` subdirectory with `.feature` files):

```bash
python3 <path-to-skill>/tools/generate-excel.py
```

The script:
- Parses all `.feature` files under `features/`
- Extracts scenario ID, persona (from `@persona:` tags), feature area, rule,
  steps, tag rationale, and all tag dimensions
- Generates an Excel workbook with: All Scenarios sheet (filterable), Summary
  sheet (per-area stats), and Instructions sheet (for manual testers)
- Outputs to `bdd-scenarios-YYYY-MM-DD.xlsx`

**Requirements:** Python 3, `xlsxwriter` (`pip install xlsxwriter`)
