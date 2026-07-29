# BDD Manifesto

## Principles

1. **Specs are the source of truth.** Tests are generated from specs, never the other way around.
2. **Specs are owned by the team, not by QA.** BA, PM, Dev, QA - all are valid authors and reviewers.
3. **LLM writes, humans validate.** No spec is authoritative without a human sign-off.
4. **Test files are build artifacts.** They are never edited directly. Changes go through the spec.
5. **Specs are implementation-agnostic.** They describe behavior, not code.

---

## Syntax

Scenarios are written in **Gherkin syntax** (plain text, no framework implied):

```
@[feature-id]-[scenario-id] @[timing] @[depth] @[criticality] @[status]
Scenario: [Short descriptive title]
  Given [initial context / preconditions]
  And   [additional context if needed]
  When  [action taken]
  Then  [expected outcome]
  And   [additional expected outcomes if needed]
```

Underlying test framework is a QA decision. Specs do not change when the framework changes.

Tags are native Gherkin syntax using `@` prefix, placed on the line above a `Scenario`. Multiple tags per scenario are allowed and expected. Reference: https://cucumber.io/docs/cucumber/api/#tags

```gherkin
@F-001-S-01 @smoke @e2e @critical @wip
Scenario: Block checkout when cart is empty
  Given the user is logged in
  And the cart is empty
  When the user clicks "Checkout"
  Then an error message is displayed
  And the checkout is not processed
```

---

## Tagging Taxonomy

Tags are proposed by LLM and confirmed by human during spec review. No scenario is committed without at least one tag from each dimension.

### Dimension 1 - Execution Timing

When the test runs in the CI/CD pipeline.

| Tag | Meaning |
|---|---|
| `@smoke` | Critical path only. Runs on every deploy. Must complete fast (seconds, not minutes). |
| `@regression` | Full behavioral coverage. Runs nightly or pre-release. |
| `@nightly` | Slow, expensive, or environment-dependent. Scheduled runs only, never on deploy. |

### Dimension 2 - Stack Depth

How much of the stack the test exercises.

| Tag | Meaning |
|---|---|
| `@e2e` | Full stack. Real backend, real browser, real data flow. |
| `@integration` | Frontend + backend contract. No full browser session required. |
| `@component` | Isolated component. Dependencies mocked. Fastest execution. |

### Dimension 3 - Criticality

What happens in CI if this test fails.

| Tag | Meaning |
|---|---|
| `@critical` | Blocks deploy unconditionally. Zero tolerance. |
| `@high` | Blocks release pipeline. Does not block hotfix deploy. |
| `@low` | Reported and tracked. Non-blocking. |

### Dimension 4 - Lifecycle Status

Where the scenario sits in its own lifecycle.

| Tag | Meaning |
|---|---|
| `@wip` | Work in progress. Excluded from all CI runs. Spec not yet approved. |
| `@flaky` | Known unstable. Runs but never blocks. Triggers a separate flakiness report. |

### Dimension 5 - Persona

Who is performing the action in the scenario. Extracted from the Feature description's "As a ..." line or the Background's actor.

Use the `@persona:<name>` colon-namespace format. The name is lowercase, hyphenated, derived from the role or actor described in the Feature block.

| Tag | Meaning |
|---|---|
| `@persona:admin` | System administrator or back-office user |
| `@persona:parent` | Parent user (in education/family contexts) |
| `@persona:teacher` | Teacher or instructor |
| `@persona:student` | Student or learner |
| `@persona:customer` | End customer or buyer |
| `@persona:guest` | Unauthenticated or anonymous user |
| `@persona:api-consumer` | External system or API client |

This is not a closed set — derive the persona from the Feature's "As a ..." line. If the Feature describes "As a warehouse manager", use `@persona:warehouse-manager`. If multiple personas interact in a single scenario, tag all of them (e.g., `@persona:parent @persona:teacher`).

### LLM Tagging Instructions

When producing a `.feature` file, LLM must:
- Propose at least one tag from each dimension (Timing, Depth, Criticality, Status, Persona)
- Default lifecycle status to `@wip` on every new scenario - human removes `@wip` on sign-off
- Extract the persona from the Feature's "As a ..." line and add as `@persona:<name>` tag — every scenario must have at least one persona tag
- Add a `# TAG RATIONALE:` comment below each scenario explaining tag choices for human review
- Flag if a scenario is ambiguous across dimensions and ask human to decide before committing

Example output before human review:
```gherkin
@wip @smoke @e2e @critical @persona:customer
Scenario: Block checkout when cart is empty
# TAG RATIONALE: smoke - core purchase flow blocker; e2e - requires real cart
#                state from backend; critical - checkout failure = zero revenue;
#                persona:customer - retail customer from Feature description
  Given the user is logged in
  And the cart is empty
  When the user clicks "Checkout"
  Then an error message is displayed
  And the checkout is not processed
```

After human approval, `@wip` is removed and the scenario is committed.

---

## Naming Conventions

### Spec Files

```
/specs/features/[feature]/[ticket-id]-[flow].feature
```

Examples:
```
/specs/features/cart/PRJ-123-checkout-flow.feature
/specs/features/user/PRJ-456-login-flow.feature
/specs/features/payments/PRJ-789-refund-flow.feature
/specs/features/user/PRJ-201-password-validation-rules.feature
```

**Rules:**
- `feature`: the feature area, kebab-case. Becomes the folder, not part of the filename.
- `ticket-id`: the originating requirement ticket ID, extracted by LLM from input at creation time. Frozen at creation. Never updated.
- `flow`: the specific workflow or rule group covered by the file, kebab-case. Use `-flow` suffix for user-facing workflows (e.g. `checkout-flow`, `login-flow`), use `-rules` suffix for validation/constraint groups (e.g. `password-validation-rules`). Groups related scenarios - not a single scenario.
- One file per ticket. Multiple related scenarios per file is correct and expected.
- Files are write-once on the name. A superseding ticket creates a new file. The old file is never renamed.
- Bug fixes do not mutate existing spec files. They add new files with the bug ticket ID.
- **A scenario belongs to the feature area that owns the behavior, not the one that triggers it.** If checkout triggers a loyalty points update, the loyalty scenario lives under `/features/loyalty/`, not `/features/cart/`.

### Test Files

Test files mirror spec file paths and names exactly:

```
/specs/features/cart/PRJ-123-checkout-flow.feature
/tests/features/cart/PRJ-123-checkout-flow.test.js
```

Every generated test file carries the following header:

```javascript
// @spec: /specs/features/cart/PRJ-123-checkout-flow.feature
// @generated: do not edit directly - changes go through the spec file
```

LLM resolves the target test file by `@spec` header first, path convention second. If neither matches, a new file is created and the orphan is flagged for human review.

### Element Identifiers (`data-testid`)

```
[feature]-[element]-[role]
```

Examples:
```
cart-error-message
checkout-submit-btn
email-input-error
login-form-password
```

This is the standard. There is no prior convention to reconcile with.

### Scenario IDs

Every scenario carries a unique project-wide ID composed of a zero-padded feature sequence number and a zero-padded scenario sequence number:

```
@F-[NNN]-S-[NN]
```

Examples:
```
@F-001-S-01    # feature 1, scenario 1
@F-001-S-02    # feature 1, scenario 2
@F-012-S-03    # feature 12, scenario 3
```

**Rules:**
- IDs are assigned at scenario creation time and never changed, even if the scenario is moved or the feature is renamed
- IDs are never reused, even if a scenario is deleted
- Feature sequence numbers are project-wide, tracked in `/specs/_index.json`
- Scenario sequence numbers are feature-scoped, tracked in `/specs/features/[feature]/_index.json`

**Tracking files:**

`/specs/_index.json` - project-wide feature counter:
```json
{ "last_feature": 3 }
```

`/specs/features/[feature]/_index.json` - per-feature scenario counter:
```json
{ "feature_id": "F-001", "feature": "cart", "last_scenario": 4 }
```

**LLM ID assignment workflow:**
1. New feature folder: read `/specs/_index.json`, increment `last_feature`, write back, assign `F-NNN` (zero-padded to 3 digits)
2. New scenario in existing feature: read `/specs/features/[feature]/_index.json`, increment `last_scenario`, write back, assign `S-NN` (zero-padded to 2 digits)
3. Both files must be updated and committed atomically with the `.feature` file

---

## Processes

### 1. New Feature Request

```
Requirement received (ticket, brief, meeting notes)
  -> LLM analyzes requirement and produces BDD scenarios
  -> Human review: BA/PM validates intent, QA validates coverage
  -> Scenarios approved and committed to repo
  -> LLM implements tests from approved scenarios
  -> Tests run in CI
```

**Rules:**
- LLM generates scenarios as part of the analysis step, not after it. Scenarios ARE the documented understanding of the requirement.
- If scenarios require clarification, clarification happens at the spec level, not in code.
- Scenarios must cover: happy path, edge cases, error/failure paths.

**LLM instructions:**
- Input: requirement text (ticket, brief, meeting notes, or any combination)
- Extract ticket ID from input - if absent, ask for it before proceeding; it is required for file naming
- Produce Gherkin scenarios covering: happy path, at least one edge case, at least one error/failure path
- For each scenario, identify which `data-testid`, `data-state`, `data-error-code`, and ARIA attributes will be required - list them as a "Contract Requirements" block at the bottom of the `.feature` file for dev reference, following the `[feature]-[element]-[role]` naming convention
- Do not infer or assume UI implementation details not present in the requirement - flag ambiguities explicitly for human resolution before proceeding
- After scenario approval: implement tests in the project's designated framework, anchoring all element lookups to `data-testid`; assert visibility using framework visibility checks, never DOM presence alone
- Output: `/specs/features/[feature]/[ticket-id]-[flow].feature` + mirrored `/tests/features/[feature]/[ticket-id]-[flow].test.js` with `@spec` and `@generated` headers

---

### 2. Bug Report

```
Bug identified
  -> Document: steps to reproduce + expected result + actual result
  -> This IS a Gherkin scenario (Given/When/Then with a failing Then)
  -> LLM formalizes it into a proper BDD scenario
  -> Human review: QA confirms the scenario captures the bug accurately
  -> Scenario committed to repo (as a failing scenario)
  -> LLM implements the test - test must fail before fix
  -> Dev fixes the bug
  -> Test passes - scenario is now part of the permanent regression suite
```

**Rules:**
- A bug without a scenario is not fully documented.
- A fix without a passing scenario is not verified.
- The bug report workflow and the spec workflow are the same workflow.

**LLM instructions:**
- Input: bug report containing steps to reproduce, expected result, actual result
- Extract ticket ID from input - if absent, ask for it before proceeding; it is required for file naming
- Formalize into a Gherkin scenario where `Then` describes the expected (correct) behavior, not the actual (broken) behavior - the scenario must read as the intended behavior, not the bug
- Add a `# BUG: [ticket-id]` comment at the top of the scenario for traceability
- Implement the test immediately - it must fail against the current codebase before the fix; flag if it does not fail (indicates the bug report is inaccurate or the bug is not reproducible)
- After dev fix: re-run test, confirm it passes, remove the `# BUG` comment, move scenario to `/specs/features/` if not already there - it is now a permanent regression scenario
- Output: `/specs/bugs/[feature]/[ticket-id]-[flow]-fix.feature` + mirrored `/tests/bugs/[feature]/[ticket-id]-[flow]-fix.test.js` with `@spec` and `@generated` headers

---

### 3. Refactor / Regression

```
Code change (refactor, dependency upgrade, architectural change)
  -> Specs are NOT touched
  -> LLM regenerates tests from existing specs targeting the updated codebase
  -> Tests run - any failure indicates a behavioral regression, not a test problem
```

**Rules:**
- If a refactor requires spec changes, it is not a refactor - it is a behavior change and must go through Process 1.
- Specs surviving a framework migration unchanged is the proof they are implementation-agnostic.

**LLM instructions:**
- Input: notification of code change (refactor, dependency upgrade, architectural change) + scope (which modules/features affected)
- Do not touch `.feature` files under any circumstance
- Regenerate test files for affected scope only, or full suite if scope is unclear
- If a test cannot be regenerated without spec changes, halt and flag to human - this is a behavior change, not a refactor
- Output: regenerated test files in `/tests/`; list any tests that required clarification

---

### 4. Framework Migration

```
Decision to migrate test framework
  -> Specs remain untouched
  -> LLM re-implements all tests in the new framework
  -> Tests run - coverage is identical by definition
  -> Old framework removed
```

This process exists and is trivial precisely because specs are the source of truth.

**LLM instructions:**
- Input: target framework name + project stack details
- Re-implement all tests from `/specs/` in the new framework; specs are the only source - do not reference old test files
- Naming, structure, and organization of test files follow the new framework's conventions
- Output: full test suite in `/tests/` for the new framework; flag any scenario that cannot be implemented in the target framework (capability gap, not a spec problem)

---

### 5. Spec Audit

**Trigger:** Quarterly, or after any major feature release.

```
LLM reviews full spec suite and flags:
  - Missing coverage (known features with no scenarios)
  - Duplicate or overlapping scenarios
  - Obsolete scenarios (features removed or changed without spec update)
  -> Human review: team confirms and acts on findings
  -> Spec suite updated
  -> Tests regenerated where affected
```

**LLM instructions:**
- Input: full `/specs/` directory + product feature list or changelog (if available)
- Produce an audit report with three sections: Missing Coverage, Duplicates/Overlaps, Obsolete Scenarios
- Do not modify any `.feature` file during audit - report only
- After human confirms findings: apply approved changes to spec files, then regenerate affected tests
- Output: `spec-audit-[date].md` report; updated `.feature` files and regenerated tests after human approval

---

### 6. Onboarding

```
New team member joins
  -> Read the spec suite before reading the code
  -> Specs are the system documentation
  -> Questions about system behavior are answered by specs first, code second
```

If a behavior exists in code but not in specs, the spec is incomplete - file it as a gap.

**LLM instructions:**
- When a new team member asks "how does X work": answer from specs, not from code
- If the question cannot be answered from specs, flag the gap and initiate a mini-audit for the relevant feature

---

### 7. Visual Regression Testing

**Trigger:** Any scenario that results in a visible UI state change (error shown, success state, empty state, disabled element, modal open, etc.)

```
BDD scenario approved
  -> LLM identifies UI states that require visual baseline capture
  -> LLM generates screenshot anchor list (which data-testid, in which state)
  -> Visual regression tool captures baseline screenshots
  -> Human (designer or QA) approves baselines
  -> On every subsequent test run: screenshots compared against approved baseline
  -> Diff above threshold -> human review required -> approve new baseline or reject change
```

**Rules:**
- Visual regression does not replace BDD scenarios. It complements them: BDD asserts behavior, visual regression asserts appearance.
- Screenshots are anchored to `data-testid`, never to CSS selectors or XPath.
- Baseline approval is always a human decision. LLM does not approve visual changes.
- Tooling choice (Percy, Chromatic, Playwright native) is a QA decision and does not affect this process.

**LLM instructions:**
- Input: approved `.feature` file
- For each scenario, identify every `Then` step that produces a visible UI state change
- Generate a screenshot capture list in the following format:

```
Scenario: [scenario title]
  Capture: [data-testid="element-id"] at state [data-state value or ARIA state]
  Capture: [data-testid="element-id"] at state [...]
```

- Do not generate baseline screenshots - that is the visual regression tool's responsibility
- Output: `[feature-name].screenshots.md` in `/specs/features/` alongside the `.feature` file

---

## Dev / Test Contracts

These are non-negotiable implementation requirements. A feature is not done unless these contracts are honored. They belong in the Definition of Done.

### Contract 1: Element Identifiers (`data-testid`)

Every interactive element and every feedback element (error messages, success states, loading indicators, empty states) must carry a `data-testid` attribute.

```html
<div data-testid="checkout-error-message">Your cart is empty</div>
<button data-testid="checkout-submit-btn">Checkout</button>
```

**Rules:**
- `data-testid` values are stable identifiers. They do not change with design refactors, CSS changes, or DOM restructuring.
- Naming convention: see Naming Conventions section above.
- Dev is responsible for adding and maintaining testids. QA is responsible for flagging missing ones.
- Tests locate elements exclusively by `data-testid`. No XPath. No CSS class selectors.

### Contract 2: Semantic State Attributes

Elements must expose their state as data attributes, not only as visual/CSS state.

```html
<div data-testid="checkout-error-message" data-state="error" data-error-code="CART_EMPTY">
  Your cart is empty
</div>
<input data-testid="email-input" aria-invalid="true" />
<button data-testid="checkout-submit-btn" aria-disabled="true" />
```

Tests assert on `data-state`, `data-error-code`, and ARIA attributes. Never on CSS class names. Never on text content.

**Standard state attributes:**
- `data-state` - current element state: `error`, `success`, `loading`, `empty`, `disabled`
- `data-error-code` - machine-readable error code (see Contract 3)
- `aria-invalid` - form field validation state
- `aria-disabled` - disabled interactive elements
- `aria-expanded` - toggleable containers (dropdowns, accordions)
- `aria-live` - dynamically updated regions

Where ARIA is already required for accessibility compliance, it serves as a test contract at no additional cost. Accessibility and testability are the same contract.

### Contract 3: API Error Response Shape

All backend error responses must include a machine-readable code alongside any human-readable message.

```json
{
  "error": {
    "code": "CART_EMPTY",
    "message": "Your cart is empty"
  }
}
```

- `code` is the stable contract identifier. It does not change with copy updates, i18n changes, or locale.
- `message` is for display only. Tests never assert on `message`.
- Frontend sets `data-error-code` from `error.code` when rendering error feedback.
- Tests assert on `data-error-code`. The full assertion chain is: API returns code -> frontend sets attribute -> test asserts attribute.

---

## Internationalization (i18n) in Tests

### Rule: Never assert on user-facing text

User-facing strings change with copy updates, locale changes, and i18n refactors. Tests that assert on string content are brittle by definition.

Assert instead on:
- `data-testid` presence and visibility
- `data-state` value
- `data-error-code` value
- ARIA state attributes

### When the message originates from the backend

Integration tests run on the frontend with no access to backend translation sources. Resolution by test type:

**Integration tests: assert on error code**
Test reads the rendered `data-error-code` attribute set by the frontend from the API response `error.code`. Message content is irrelevant.

**E2E tests (full stack): assert on presence only**
Real backend, real locale. Assert that the error element is visible with the correct `data-state`. Do not assert on message content.

---

## Repository Structure

```
/specs
  _index.json                                       # project-wide feature counter
  /features
    /[feature]
      _index.json                                   # per-feature scenario counter
      [ticket-id]-[flow].feature                    # Gherkin scenario files
      [ticket-id]-[flow].screenshots.md             # Visual regression anchor list
  /bugs
    /[feature]
      [ticket-id]-[flow]-fix.feature                # Bug scenarios, permanent after fix
  /audits
    spec-audit-[date].md                            # Audit reports
/tests
  /features
    /[feature]
      [ticket-id]-[flow].test.js                    # generated - do not edit directly
  /bugs
    /[feature]
      [ticket-id]-[flow]-fix.test.js                # generated - do not edit directly
```

---

## Addendum: Future Improvements

These are validated ideas not yet implemented. They do not change the current modus operandi. They are recorded here to prevent reinvention and to guide the next evolution of this process.

### A. Ticket as Prompt

The natural evolution of Process 1 is that the ticket itself becomes the LLM prompt, with no human reformulation required. LLM reads the ticket directly and extracts: ticket ID, feature context, acceptance criteria, edge cases. Zero additional input from the human initiating the process.

Implication: CI/CD pipeline can trigger spec generation automatically on ticket status change (e.g. "In Progress" or "Ready for Dev"). Example flow:
```
Ticket status -> "In Progress"
  -> Webhook triggers LLM
  -> LLM reads ticket, generates draft .feature files (one per scenario)
  -> Draft spec opened as PR for human review
  -> Approved PR = spec committed = process continues as normal
```

This makes BDD spec generation a fully automated pipeline step, not a manual one. Human effort reduces to review and approval only.

### B. Spec Generation as a CI/CD Pipeline Stage

Extends A. Spec review, test generation, and visual regression anchor list generation become pipeline stages with PR gates. No manual triggering required at any step.

---

## Accountability

| Activity | LLM | BA / PM | Dev | QA | Approver |
|---|---|---|---|---|---|
| Write scenarios (feature) | Author | Reviewer | - | Reviewer | QA + BA |
| Write scenarios (bug) | Author | - | - | Reviewer | QA |
| Implement tests | Author | - | - | Reviewer | - |
| Generate Contract Requirements | Author | - | Receiver | - | - |
| Implement testids / state attributes | - | - | Author | Auditor | - |
| Regenerate tests (refactor) | Author | - | - | Reviewer | - |
| Re-implement tests (migration) | Author | - | - | Reviewer | - |
| Spec audit | Author | Reviewer | - | Reviewer | Team Lead |
| Generate screenshot anchor list | Author | - | - | Reviewer | - |
| Approve visual baselines | - | - | - | Author | Designer / QA |
| Onboarding guidance | Author | - | - | - | - |
