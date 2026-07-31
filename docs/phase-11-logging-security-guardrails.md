# Phase 11: Logging, security, and guardrails

## Outcome

Phase 11 places one operational boundary around every browser and API request.
It improves traceability and failure safety without changing catalog,
recommendation, retrieval, AI, or audio-analysis behavior.

## Request tracing and logs

Every response receives a new server-generated UUID in `X-Request-ID`.
Structured JSON logs contain the request ID, method, path, status, duration,
severity, logger, and event message. Query text, request bodies, raw prompts,
audio bytes, cookies, authorization values, and API keys are not logged.

Unexpected exceptions are logged server-side with their exception type and
request ID. The public response contains only a safe message and that same ID,
allowing support investigation without returning stack traces or secrets.

## HTTP guardrails

- Declared request bodies over 26 MiB are rejected with `413` before parsing.
- Mutating requests with a foreign `Origin` are rejected with `403`.
- Request IDs supplied by callers are ignored to prevent log spoofing.
- Existing Pydantic, prompt-length, upload-format, ownership, and catalog
  grounding checks remain the domain-level validation layer.

The body limit is one MiB larger than the 25 MiB audio-file limit so normal
multipart framing can pass to the stricter audio validator.

## Browser security headers

All responses include:

- `Content-Security-Policy` restricted to same-origin application resources;
- `X-Content-Type-Options: nosniff`;
- `X-Frame-Options: DENY`;
- `Referrer-Policy: no-referrer`;
- a `Permissions-Policy` disabling camera, microphone, and geolocation.

Private-song cookies already use `HttpOnly`, `SameSite=Strict`, and `Secure`
in production.

## Deployment boundary

Application checks are defense in depth. A production deployment should still
apply TLS, trusted-host validation, rate limiting, request limits, log
retention, monitoring, and secret rotation at the reverse proxy or hosting
platform. Those controls require the real deployment hostname and service.

## Verification

Integration tests verify unique UUIDs, security headers, cross-origin and body
rejection, prompt omission from logs, and safe traceable unexpected errors.
