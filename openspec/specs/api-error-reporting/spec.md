# api-error-reporting Specification

## Purpose

Defines how libtado reports failures and progress to the program embedding it: typed exceptions that callers can handle precisely, and diagnostics emitted through standard logging, so the library never writes to stdout or terminates the host process.

## Requirements

### Requirement: Common exception base
Every error the library raises on its own behalf (HTTP failures, rate limiting, authentication problems) SHALL be an instance of a single library exception type, so callers can catch all library failures with one `except` clause.

#### Scenario: Catch-all handling
- **WHEN** an API call fails with an HTTP error, a rate-limit error or an authentication-flow error
- **THEN** each of these errors is an instance of the library's common exception type

### Requirement: HTTP errors remain compatible with requests
Errors raised for a non-success HTTP response SHALL expose the HTTP status code and the response, and SHALL also be catchable as `requests.exceptions.HTTPError`, so code written against earlier versions keeps working.

#### Scenario: Legacy handler still works
- **WHEN** an API call receives HTTP 404 or 500 and the caller wraps it in `except requests.exceptions.HTTPError`
- **THEN** the handler is invoked

#### Scenario: Status code available
- **WHEN** an API call fails with HTTP 400
- **THEN** the raised error exposes the status code 400 and the response that caused it

### Requirement: Dedicated rate-limit error
A request that stays rate-limited after the retry policy has been applied SHALL raise an error that is distinguishable from other HTTP errors and that exposes the wait reported by the server, when there is one.

#### Scenario: Distinguish rate limiting from other failures
- **WHEN** a call fails because of HTTP 429 after the retry policy is applied
- **THEN** the raised error is the dedicated rate-limit error, which is still catchable as a generic HTTP error

#### Scenario: Reported wait is exposed
- **WHEN** the 429 response carried `Retry-After: 3600`
- **THEN** the raised rate-limit error exposes a wait of 3600 seconds

### Requirement: Authentication flow errors
Problems in the OAuth device-code login flow (flow started twice, flow not started, verification code expired before the user logged in) SHALL be raised as an authentication error, and the library SHALL NOT terminate the host process in any of these cases.

#### Scenario: Device code expired
- **WHEN** the Tado login service reports that the device code has expired while the library is waiting for the user
- **THEN** an authentication error is raised and the process keeps running

#### Scenario: Flow started twice
- **WHEN** the device login flow is started on a client whose flow has already been started
- **THEN** an authentication error is raised whose message states that the flow was already started

#### Scenario: Activation before start
- **WHEN** device activation is requested before the device flow has been started
- **THEN** an authentication error is raised whose message states that the flow has not yet started

### Requirement: Diagnostics through logging
The library SHALL emit its diagnostics (login progress, verification URL, rate-limit waits and retries, schedule warnings) through the standard `logging` module under the `libtado` logger name, and SHALL NOT write to standard output or standard error directly, so embedding applications control where messages go.

#### Scenario: No stdout noise during API use
- **WHEN** a client performs ordinary API calls or hits a rate-limit retry
- **THEN** nothing is written to standard output, and a retry is reported as a log record on the `libtado` logger

#### Scenario: Silent by default
- **WHEN** the embedding application has not configured logging
- **THEN** the library emits no output at INFO level or below

#### Scenario: Verification URL stays retrievable
- **WHEN** the device login flow has started
- **THEN** the verification URL is available from the client's accessor for it and is also logged

### Requirement: Invalid arguments are rejected explicitly
Calls made with an unsupported argument value SHALL raise a standard `ValueError` instead of printing a message and returning `None`.

#### Scenario: Unsupported schedule type
- **WHEN** the schedule blocks of a zone are set with a schedule identifier other than 0, 1 or 2
- **THEN** a `ValueError` is raised and no request is sent

### Requirement: Warnings for partial results and deprecation
Day types that cannot be applied to the selected schedule SHALL be reported as a logged warning while the compatible day types are still applied, and use of a deprecated method SHALL raise a Python `DeprecationWarning`.

#### Scenario: Some day types are inapplicable
- **WHEN** schedule blocks are set with a day type that is not valid for the chosen schedule, together with valid ones
- **THEN** the valid day types are sent, and a warning naming the skipped day types is logged

#### Scenario: Deprecated method
- **WHEN** the deprecated per-day-type schedule setter is called
- **THEN** a `DeprecationWarning` is issued and the call is forwarded to its replacement

### Requirement: Command line client presents errors cleanly
The command line client SHALL print the login verification URL and wait for activation itself, and SHALL convert library errors into a one-line message with a non-zero exit status instead of a stack trace.

#### Scenario: First login from the CLI
- **WHEN** the CLI starts with no usable token and the login flow is pending
- **THEN** the verification URL is shown to the user on the terminal and the CLI waits for activation

#### Scenario: Rate-limited command
- **WHEN** a CLI command fails because the API is rate-limited for longer than the maximum wait
- **THEN** the CLI prints a single-line error mentioning the rate limit and exits with a non-zero status
