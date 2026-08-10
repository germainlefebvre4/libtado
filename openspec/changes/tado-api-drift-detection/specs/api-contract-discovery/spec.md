## Purpose

Captures the real shape of the live Tado API into cumulative, privacy-safe artifacts (schemas and cassettes) that can serve as an offline contract, without ever writing real personal data to a versioned file.

## ADDED Requirements

### Requirement: Cumulative schema construction
Discovery SHALL merge each newly observed response shape into the previously committed schema for that endpoint, rather than replacing the schema from a single sample.

#### Scenario: New field appears in a live response
- **WHEN** discovery observes a field that is not present in the committed schema for an endpoint
- **THEN** the updated schema includes the new field in addition to every field already present in the committed schema

#### Scenario: A previously observed field is absent from the current sample
- **WHEN** discovery captures a response that omits a field previously recorded in the committed schema
- **THEN** the updated schema still includes that field, since the schema represents the union of every shape ever observed

### Requirement: Deterministic anonymization before persistence
Discovery SHALL replace real values that could identify a person, home, or account (geolocation, device/installation identifiers, serial numbers, names, emails, addresses) with a fake value before writing any artifact to disk, and SHALL derive each fake value deterministically from the field's path so unchanged real data always produces the same fake value.

#### Scenario: Repeated run against unchanged real data
- **WHEN** discovery is run twice in a row against a live account whose data has not changed
- **THEN** the anonymized artifacts produced by both runs are byte-for-byte identical

#### Scenario: A response contains personal data
- **WHEN** discovery captures a response containing a field such as geolocation coordinates, a device serial number, an installation ID, a name, or an email address
- **THEN** the value written to any versioned artifact is a generated fake value, never the real value

### Requirement: Mutating endpoints excluded from unattended runs
Discovery SHALL only invoke read-only endpoints during an unattended (scheduled) run. Mutating endpoints SHALL only be invoked when explicitly requested as part of a manually triggered run.

#### Scenario: Unattended run
- **WHEN** discovery executes as part of an unattended/scheduled trigger
- **THEN** only read-only endpoints are called; no endpoint that writes to the live account is invoked

#### Scenario: Manual run with mutating endpoints requested
- **WHEN** a human explicitly triggers discovery and opts in to including mutating endpoints
- **THEN** mutating endpoints may be invoked as part of that run

### Requirement: Replayable cassette capture
For each live call it makes, discovery SHALL record the request and its anonymized response as a cassette artifact that can be replayed offline without network access or live credentials.

#### Scenario: Cassette produced from a live call
- **WHEN** discovery successfully calls a live endpoint
- **THEN** a cassette artifact is written for that call containing no real personal data, and that artifact can be replayed to reproduce the same response without contacting the live API
