# claude-atdd

A plugin marketplace for ATDD (acceptance-test-driven design/development).
It works with both Claude Code and OpenAI Codex.

## Vision

The goal is a full ATDD framework for creating and maintaining acceptance
tests from change requests, existing code, and documentation - spanning
feature creation, TDD, BDD, and integration/e2e testing.

Today this ships the BDD-authoring half of that workflow: Gherkin spec
authoring/generation and persona-based flow auditing. TDD and integration/e2e
testing support are planned as later additions.

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

## Plugins in this marketplace

| Plugin | Description |
|---|---|
| [`atdd`](./plugins/atdd) | ATDD toolkit - Gherkin spec authoring, scenario generation, test implementation, bug documentation, spec auditing, persona operations mapping, and visual regression anchoring. See [plugins/atdd/README.md](./plugins/atdd/README.md) for full details. |

## Repository layout

Each tool reads its own manifests:

| Tool | Marketplace | Plugin manifest |
|---|---|---|
| Claude Code | `.claude-plugin/marketplace.json` | `plugins/<name>/.claude-plugin/plugin.json` |
| Codex | `.agents/plugins/marketplace.json` | `plugins/<name>/.codex-plugin/plugin.json` |

Both tools load the same `skills/` folder. When you change a name, version,
or description, change both sets of manifests. Then run the sync check:

```
python3 scripts/check-manifests.py
```

## License

[MIT](./LICENSE)
