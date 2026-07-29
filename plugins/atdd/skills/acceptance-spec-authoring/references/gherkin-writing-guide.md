# Gherkin Writing Guide

Reference: https://testquality.com/examples-of-good-vs-bad-gherkin-test-scenarios-a-guide-to-better-bdd-testing/

This guide defines how to write good Gherkin scenarios. Apply these rules
on every scenario produced. They complement the manifesto contracts - the
manifesto defines what to assert, this guide defines how to write the spec.

---

## Core Principles

### 1. Declarative, Not Imperative

Describe what the system does, not how the user does it.
Never reference UI elements, selectors, URLs, or button labels in a scenario.

BAD:
```gherkin
When I click on the element with ID "checkout-btn"
And I type "testuser" into the input field
Then I should see the URL change to "/dashboard"
```

GOOD:
```gherkin
When the user submits valid login credentials
Then they should be redirected to their dashboard
```

### 2. One Behavior Per Scenario

Each scenario tests exactly one behavior. If a scenario has multiple
When/Then blocks, it is testing multiple behaviors. Split it.

BAD:
```gherkin
Scenario: Complete registration and first purchase
  When I fill out the registration form
  Then I should see a welcome message
  When I add a product to the cart
  Then I should receive an order confirmation
```

GOOD:
```gherkin
Scenario: Successful account registration
  When a new user registers with valid information
  Then their account should be created successfully

Scenario: Order confirmation after purchase
  Given a registered customer has items in their cart
  When they complete the checkout
  Then they should receive an order confirmation
```

### 3. Group Related Scenarios in the Same File

Scenarios that share the same Feature block, Background, or business rule
belong in the same file. Do not split them artificially.

The filename reflects the ticket and the flow or rule group - not a single
scenario. Multiple related scenarios per file is correct and expected.

```
/specs/features/cart/PRJ-123-checkout-flow.feature        # happy path, empty cart, payment failure
/specs/features/user/PRJ-789-password-validation-rules.feature # length, uppercase, special char rules
```

Use `-flow` for user-facing workflows, `-rules` for validation/constraint groups.

If a feature file is growing large, that is a signal the ticket was too broad,
not a reason to split scenarios into individual files. Use the Rule keyword
to organize groups of scenarios within a file before considering a split.

### 4. Business Language Only

Scenarios are read by BA, PM, QA, and Dev. Write for the least technical
reader. If a non-technical stakeholder cannot understand a step, rewrite it.

### 5. Specific, Meaningful Data

Use concrete values instead of placeholders. Concrete values make scenarios
realistic and reviewable. Use stable test fixtures for specific values -
never rely on volatile production data.

BAD:
```gherkin
Given I have some data
When I perform some action
```

GOOD:
```gherkin
Given customer "Sarah Johnson" has placed order #12345 for $127.99
When she views her order history
Then she should see order #12345 listed with amount $127.99
```

### 6. Scenario Naming: Business Outcome, Not Test Action

BAD: `Scenario: Test shipping calculation for premium users`
GOOD: `Scenario: Premium member receives free shipping`

---

## Feature File Structure

### Feature Description

Every `.feature` file opens with a Feature block describing business value:

```gherkin
Feature: Customer Loyalty Points

  As a retail customer
  I want to earn and redeem loyalty points
  So that I receive rewards for frequent purchases
```

### Background

Use Background for static preconditions shared across scenarios in the same
feature area. Do not use Background for actions that change shared data.

```gherkin
Background:
  Given customer "Maria Lopez" is logged into her account
  And she has a valid payment method on file
```

### Rule Keyword

Use Rule to group scenarios that share the same business rule:

```gherkin
Feature: Customer Loyalty Points

  Rule: Earning points
    Scenario: Earn 1 point per dollar spent
      ...

  Rule: Redemption threshold
    Scenario: 100 points equals $5 credit
      ...

  Rule: Point expiration
    Scenario: Points expire after 12 months of inactivity
      ...
```

---

## Advanced Syntax

### Scenario Outline (Examples Tables)

Use when the same behavior needs testing with multiple inputs:

```gherkin
Scenario Outline: Password validation rules
  Given a user is creating a new account
  When they enter "<password>" as their password
  Then they should see "<result>"

  Examples:
    | password    | result                   |
    | abc123      | Password too short        |
    | password123 | Password needs uppercase  |
    | Password123 | Password accepted         |
```

### Data Tables

Use for complex structured inputs:

```gherkin
Scenario: Bulk user import
  Given the admin is importing new users
  When they upload a file containing:
    | Name        | Email             | Department |
    | Alice Brown | alice@example.com | Marketing  |
    | Bob Wilson  | bob@example.com   | Sales      |
  Then all users should be created successfully
```

### Doc Strings

Use for multi-line text inputs:

```gherkin
Scenario: Customer submits a support request
  Given a customer needs technical help
  When they submit a ticket with details:
    """
    App crashes when uploading photos larger than 5MB.
    Device: iPhone 13 Pro, iOS 17.2, App Version 3.1.4
    """
  Then a support ticket should be created
```

---

## Self-Check Before Committing a Scenario

- [ ] Does it describe behavior, not UI steps?
- [ ] Does it test exactly one behavior?
- [ ] Can a non-technical stakeholder read and validate it?
- [ ] Does it use specific, concrete data?
- [ ] Does the title describe a business outcome, not a test action?
- [ ] Is the Feature block present with As a / I want / So that?
- [ ] Are tags from all five dimensions present? (see manifesto Tagging Taxonomy)
- [ ] Is `@persona:<name>` tag present? (extracted from Feature's "As a ..." line)
- [ ] Is `@wip` present pending human approval?
- [ ] Is `# TAG RATIONALE:` present?
- [ ] Is the Contract Requirements block present?
