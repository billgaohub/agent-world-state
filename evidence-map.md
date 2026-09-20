# Evidence Map & Demarcation Boundary

## Abstract Evidence Locators

In `agent-world-state`, physical evidence is never bundled directly into the specification or public repositories. Instead, observations reference external artifacts using standardized abstract locators:

1. **URI Locators (`uri:<url>`)**
   - Canonical public or private endpoints.
   - Example: `uri:https://www.bilibili.com/video/BV19fYf6kELz#t=00:48:30`
   - Example: `uri:https://mimo.xiaomi.com/rl/api/notices`

2. **Content Hash Locators (`sha256:<hash>`)**
   - Cryptographic fingerprint of raw payloads, frames, or telemetry exports stored in designated evidence archives.
   - Example: `sha256:7d245e1aac5f00c5fbd6a1475e5f5d4c1b09b54996eaae3c8d5bc910f2a75f9e`

3. **Stream Offset Locators (`offset:<stream_id>#<timestamp>`)**
   - Temporal positions in recorded media or simulation steps.
   - Example: `offset:stream-live-day1#00:48:30`

## Single Source of Truth (SSOT) Contract

The `agent-world-state` specification is strictly governed by the following SSOT boundary axiom:

> **`agent-world-state never owns field-study facts.`**

### Boundary Roles & Responsibilities

| Domain | Authority Type | Responsibilities |
|---|---|---|
| **Upstream Field Studies / Repositories** | **Factual Authority** | Captures raw logs, video media, sensor streams, API dumps, and domain-specific transcripts. Upstream owns ground reality. |
| **`agent-world-state` Specification & Validator** | **Derived Model Authority** | Defines canonical schemas, validation logic, orthogonal epistemic axes, temporal decoupling rules, and verification pipelines. Does not retain raw field data. |

### Upstream Drift Invalidation Protocol

When an upstream source revises its raw data or corrects an event:
1. The upstream repository updates its factual record and emits a new digest.
2. The observing system detects `STALE_SOURCE_DRIFT`.
3. Downstream claims are marked as requiring re-verification.
4. An immutable `Correction` record is appended referencing the revised upstream digest.
5. Prior historical observations remain unmutated in the audit log.
