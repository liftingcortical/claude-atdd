# claude-atdd

A Claude Code plugin marketplace for ATDD (acceptance-test-driven
design/development).

## Vision

The goal is a full ATDD framework for creating and maintaining acceptance
tests from change requests, existing code, and documentation - spanning
feature creation, TDD, BDD, and integration/e2e testing.

Today this ships the BDD-authoring half of that workflow: Gherkin spec
authoring/generation and persona-based flow auditing. TDD and integration/e2e
testing support are planned as later additions.

## Install

```
/plugin marketplace add liftingcortical/claude-atdd
/plugin install atdd@claude-atdd
/reload-plugins
```

## Plugins in this marketplace

| Plugin | Description |
|---|---|
| [`atdd`](./plugins/atdd) | ATDD toolkit - Gherkin spec authoring, scenario generation, test implementation, bug documentation, spec auditing, persona operations mapping, and visual regression anchoring. See [plugins/atdd/README.md](./plugins/atdd/README.md) for full details. |

## License

[MIT](./LICENSE)
