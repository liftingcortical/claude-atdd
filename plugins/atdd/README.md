# ATDD Plugin

Acceptance-test-driven design/development (ATDD) toolkit. Today it implements
the BDD Manifesto workflow for spec authoring, test generation, bug
documentation, spec auditing, and visual regression anchoring, using Gherkin
as the concrete acceptance-test format. TDD and integration/e2e testing
support are planned as later additions to the same toolkit.

## Install

### Claude Code

```
/plugin marketplace add liftingcortical/claude-atdd
/plugin install atdd@claude-atdd
/reload-plugins
```

### Codex

```
codex plugin marketplace add liftingcortical/claude-atdd
codex plugin add atdd@claude-atdd
```

Restart Codex after install so it loads the skills.

## What it does

Triggers automatically on any ATDD/BDD-related request:
writing specs, creating Gherkin scenarios, implementing tests from specs,
documenting a bug as a scenario, auditing a spec suite, or anything
involving acceptance-test-driven design/development and the BDD Manifesto
workflow.

## Skills

### `acceptance-spec-authoring` — BDD Manifesto Workflow

Core skill for spec authoring, test generation, and BDD processes 1-7.

- **New feature** - analyzes requirement, generates tagged Gherkin scenarios
- **Bug report** - formalizes bug as a failing BDD scenario
- **Refactor** - regenerates tests from specs, no spec edits
- **Framework migration** - re-implements tests in new framework
- **Spec audit** - flags missing coverage, duplicates, obsolete scenarios
- **Onboarding** - answers system behavior questions from specs
- **Visual regression** - generates screenshot anchor lists per scenario

### `persona-flow-audit` — Persona Operations Map

Specialized audit that maps critical flows per persona. Reviews all specs and
application code to produce a complete operations map: who does what, in what
order, and where the gaps are.

- Extracts all personas from `@persona:` tags
- Reviews code to understand architecture and RBAC
- Constructs dependency-ordered flows per persona
- Detects wrong tags, missing scenarios, orphaned personas
- Output: `specs/audits/persona-operations-map-[date].md`

## Reference

Full BDD Manifesto: `skills/acceptance-spec-authoring/references/bdd-manifesto.md`
Gherkin writing guide: `skills/acceptance-spec-authoring/references/gherkin-writing-guide.md`
Output template: `skills/persona-flow-audit/references/output-template.md`

## Project instructions template

Copy one of these files to the root of your project. It tells the agent to
always use the `acceptance-spec-authoring` skill:

- Claude Code: `skills/acceptance-spec-authoring/references/CLAUDE.md`
- Codex: `skills/acceptance-spec-authoring/references/AGENTS.md`
