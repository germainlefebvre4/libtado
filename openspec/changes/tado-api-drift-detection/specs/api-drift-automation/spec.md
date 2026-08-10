## Purpose

Triggers the discovery mechanism automatically and on demand, surfaces detected API drift as a reviewable pull request, and lets pull request checks validate library behavior without needing live Tado credentials.

## ADDED Requirements

### Requirement: Scheduled drift check
The system SHALL run discovery automatically on a weekly schedule, without human intervention, restricted to read-only endpoints.

#### Scenario: Weekly schedule fires
- **WHEN** the weekly scheduled trigger runs
- **THEN** discovery executes against read-only endpoints only, and the freshly captured schemas/cassettes are compared against the committed ones

### Requirement: Manual on-demand run
The system SHALL allow a human to trigger discovery on demand, with read-only endpoints included by default and mutating endpoints included only when explicitly opted in.

#### Scenario: Manual trigger, default scope
- **WHEN** a human manually triggers the discovery workflow without opting in to mutating endpoints
- **THEN** only read-only endpoints are exercised

#### Scenario: Manual trigger, mutating endpoints opted in
- **WHEN** a human manually triggers the discovery workflow and explicitly opts in to mutating endpoints
- **THEN** mutating endpoints are also exercised

### Requirement: Automated drift pull request
When a scheduled run detects a difference between freshly captured schemas/cassettes and the committed ones, the system SHALL open a pull request containing the updated artifacts. It SHALL NOT merge that pull request automatically.

#### Scenario: Drift detected
- **WHEN** a weekly scheduled run produces schemas or cassettes that differ from what is committed
- **THEN** a pull request is opened containing the updated schemas and cassettes, and no automatic merge occurs

#### Scenario: No drift detected
- **WHEN** a weekly scheduled run produces schemas and cassettes identical to what is committed
- **THEN** no pull request is opened and no other action is taken

### Requirement: Credential-free pull request validation
Pull request checks, including checks on an automated drift pull request, SHALL validate library behavior by replaying committed cassettes and SHALL NOT require live Tado credentials to run or pass.

#### Scenario: Pull request from a fork
- **WHEN** a pull request is opened from a fork that has no access to live Tado credentials
- **THEN** the pull request's test checks run to completion using cassette replay and report a pass/fail result
