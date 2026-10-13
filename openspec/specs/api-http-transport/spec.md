# api-http-transport Specification

## Purpose

Defines how libtado sends requests to the Tado cloud: one consistent pipeline for every Tado host, connection reuse, and bounded automatic handling of rate-limit responses so callers do not have to re-implement it.

## Requirements

### Requirement: Uniform request behavior across Tado hosts
Every call to a Tado host (the main API, acme, minder, energy-insights and energy-bob) SHALL apply the same authentication headers, timeout, token refresh, rate-limit bookkeeping and error handling, regardless of which host the call targets.

#### Scenario: Same behavior on every host
- **WHEN** a request to any of the five Tado hosts returns a response carrying `ratelimit` and `ratelimit-policy` headers
- **THEN** the values returned by the client's rate-limit information reflect those headers, exactly as they do for the main API host

#### Scenario: Expired access token before a call
- **WHEN** the access token has expired and any endpoint method is called
- **THEN** the token is refreshed before the request is sent, whichever host the endpoint targets

#### Scenario: Error response on a secondary host
- **WHEN** a request to the acme, minder, energy-insights or energy-bob host returns a non-success status
- **THEN** the caller receives the same kind of exception as for a failure on the main API host

### Requirement: Preserved request and response semantics
Unifying the request pipeline SHALL NOT change what any existing endpoint method sends or returns: HTTP method, URL, JSON body, and the decoded response (or `None` for a 204 response where it is returned today).

#### Scenario: Existing endpoint still returns decoded JSON
- **WHEN** an existing read endpoint such as the zones listing is called against a mocked 200 JSON response
- **THEN** the method returns the decoded JSON body unchanged

#### Scenario: No-content response
- **WHEN** a mutating endpoint that currently returns `None` on HTTP 204 receives a 204 response
- **THEN** the method still returns `None`

### Requirement: Session reuse
A client instance SHALL reuse a single HTTP session for all its API calls so connections can be pooled, and the session SHALL be created on first use so a client can operate without its constructor having performed any network I/O.

#### Scenario: Several calls on one client
- **WHEN** a client makes several API calls in a row
- **THEN** all of them are sent through the same HTTP session

#### Scenario: Client built without constructor I/O
- **WHEN** a client is instantiated in a state where no session has been created yet and an endpoint method is called
- **THEN** the session is created transparently and the call succeeds

### Requirement: Automatic retry on rate limiting
When the Tado API answers HTTP 429 with a wait indication (the reset time in the `ratelimit` header, or a `Retry-After` value) that does not exceed the configured maximum wait, the client SHALL wait for that duration and resend the request, up to the configured maximum number of retries.

#### Scenario: Short rate limit then success
- **WHEN** a request is answered with 429 and `Retry-After: 2`, and the retry is answered with 200
- **THEN** the client waits about 2 seconds, resends the request, and returns the successful response to the caller without raising

#### Scenario: Retry-After as an HTTP date
- **WHEN** a 429 response carries `Retry-After` as an HTTP date within the allowed maximum wait
- **THEN** the client waits until that date and retries

#### Scenario: Wait advertised through the ratelimit header
- **WHEN** a 429 response has a `ratelimit` header giving a reset time within the allowed maximum wait (and no `Retry-After`)
- **THEN** the client waits for that reset time and retries

#### Scenario: Rate-limit information updated by a 429 response
- **WHEN** a request is answered with 429 carrying `ratelimit` and `ratelimit-policy` headers
- **THEN** the client's rate-limit information reflects those headers, even though the call then fails or is retried

#### Scenario: Retries exhausted
- **WHEN** every attempt up to the maximum number of retries is answered with 429
- **THEN** the client stops retrying and raises a rate-limit error

### Requirement: Fail fast when the wait is too long
When a 429 response indicates a wait longer than the configured maximum wait (for example an exhausted daily quota), or gives no usable wait duration (neither `Retry-After` nor a reset time in the `ratelimit` header), the client SHALL NOT sleep or retry and SHALL raise a rate-limit error immediately.

#### Scenario: Daily quota exhausted
- **WHEN** a request is answered with 429 and a `Retry-After` of several hours
- **THEN** the call raises a rate-limit error at once, without sleeping, and the error exposes the reported wait

#### Scenario: 429 without any wait information
- **WHEN** a request is answered with 429 carrying neither a `Retry-After` header nor a reset time in the `ratelimit` header
- **THEN** the call raises a rate-limit error at once, without sleeping

### Requirement: Configurable retry policy
The client SHALL let callers set the maximum number of retries and the maximum acceptable wait when constructing it, with defaults that keep a rate-limited call from blocking for long, and SHALL allow retries to be disabled.

#### Scenario: Retries disabled
- **WHEN** a client is created with the maximum number of retries set to 0 and a request is answered with 429
- **THEN** the call raises a rate-limit error immediately without resending the request

#### Scenario: Default policy
- **WHEN** a client is created without any retry option
- **THEN** it retries a 429 only when the advertised wait is short, and gives up otherwise

### Requirement: Retries limited to rate-limited requests
The client SHALL retry only requests answered with HTTP 429; other failures (4xx, 5xx, connection errors, timeouts) SHALL be reported to the caller without automatic retry.

#### Scenario: Server error
- **WHEN** a request is answered with HTTP 500
- **THEN** it is sent exactly once and the caller receives an error

#### Scenario: Mutating request throttled
- **WHEN** a PUT request is answered with 429 and then succeeds on retry
- **THEN** the PUT is applied once from the caller's point of view and its result is returned
