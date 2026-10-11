# agent-world-state Specification (v0.2.0-draft)

**Status**: EXPERIMENTAL / EMPIRICALLY_DERIVED  
**Lineage**: Derived from 2 heterogeneous field studies (GrokBot multimodal live broadcast and Xiaomi MiMo-V2.6 distributed RL training infrastructure); not an arbitrary universal standard.  
**Author**: Bill Gao & Autonomous Agentic Reviewer Protocol  
**Date**: 2026-09-20  

---

## 1. Scope and Core Axioms

The `agent-world-state` specification defines a canonical, minimal representation for autonomous agent observation ledgers, external world telemetry, and epistemic audit pipelines.

### Core Axiom: Decoupled Factual Authority
> **`agent-world-state never owns field-study facts.`**  
> Upstream systems, sensors, broadcasts, and domain repositories hold factual authority. `agent-world-state` provides the derived model authority for structuring, auditing, verifying, and revising those observations.

### Critical Epistemic Distinction: Immutability vs. Decay

To maintain consistency across multi-agent state governance, this specification strictly distinguishes between raw evidence records and downstream propositional claims:

```text
Raw evidence record
= immutable / historically fixed

Claim validity / freshness / context / coverage
= may decay or become stale

Source revision
→ STALE_SOURCE_DRIFT
→ re-verification
→ Correction
```

1. **Raw Evidence Immutability**:  
   An atomic observation record (`Observation`) captures what was physically recorded by an observer at a specific collector timestamp. Historical physical events do not change retroactively. Once committed with cryptographic hashing, raw observation records must never be modified or deleted.
2. **Propositional & Contextual Decay**:  
   Unlike raw records, the truth value, relevance, freshness, and applicability of a `Claim` are dynamic. Claims are subject to:
   - **Fact Decay**: Underlying physical facts may change in the external environment.
   - **Context Drift**: Environmental boundaries, system versions, or agent assumptions shift.
   - **Coverage Expiration**: A time window for an assertion elapses.
   - **Consensus & Ranking Shifts**: Multi-agent arbitration or fresh evidence revises confidence.
3. **Source Revision & Drift Loop**:  
   When an upstream source updates its baseline or emits an erratum, downstream systems detect `STALE_SOURCE_DRIFT`. This triggers re-verification and emits an immutable `Correction` record without rewriting historical observations.

---

## 2. The Three Orthogonal Epistemic Axes

Historical audit failures frequently stem from collapsing distinct epistemological properties into scalar "trust levels" or monolithic labels. `agent-world-state` enforces three orthogonal dimensions:

```text
       Source Authority (Origin Standing)
             ▲
             │
             │   ▲ Review Depth (Observer Rigor)
             │  /
             │ /
             └──────────────► Temporal Integrity (Decoupled Timeline)
```

### Axis 1: Source Authority (`source_authority`)
Measures the standing and directness of the origin:
- `PRIMARY`: Origin system, authoritative production API, official canonical broadcast.
- `MIRROR`: Synchronized or byte-identical redistribution of primary data.
- `SECONDARY`: Third-party summary, commentary, or news aggregators.
- `LOCAL_BASELINE`: Local test mock, isolated container, or synthetic baseline.
- `primary_permalink_pinned`: `true` only when an immutable first-party permalink is pinned.

### Axis 2: Review Depth (`review_depth`)
Measures the physical rigor executed by the observing agent:
- `identity_pinned`: Source location, endpoint, or broadcast ID physically verified.
- `metadata_verified`: Headers, content length, video duration, or schema verified.
- `content_reviewed`: Payload body, audio track, video frames, or DOM text directly inspected.
- `evidence_modalities`: Composable list of inspected interaction types (`FRAME_EXTRACTION`, `VISUAL_INSPECTION`, `BURNED_SUBTITLE_REVIEW`, `AUDIO_STREAM_PLAYBACK`, `REST_JSON_PAYLOAD`, `STATUS_EVENT_SEQUENCE`, `DOM_TEXT_SCRAPE`, `SEARCH_QUERY_CORROBORATION`).

### Axis 3: Temporal Integrity (`temporal_context`)
Decouples distinct timeline dimensions to prevent observer latency and UI clock offsets from being misattributed to event occurrence:
- `absolute_event_time`: System origin epoch (ISO 8601 UTC).
- `relative_source_offset`: Stream offset (`T+00:48:30`) or training step offset (`step: 15`).
- `collector_time`: Wall clock of the observing agent when recording observation (mandatory).
- `published_or_observed_clock`: External display timestamp visible on UI headers.
- `clock_skew_seconds`: Computed delta between published clock and source event epoch.
- `skew_status`: `VALID`, `CALIBRATED_WITH_DISCREPANCY_EXPLAINED`, `UNKNOWN_SKEW`, `NOT_APPLICABLE`.

---

## 3. Atomic Entity Definitions

### 3.1 Observation
Atomic unit of empirical telemetry:
- `observation_id`: Unique identifier (e.g. `OBS-GROKBOT-008`).
- `observation_kind`: One of `ACTION`, `STATE_CHANGE`, `FAILURE`, `INTERVENTION`, `RECOVERY`, `SPOKEN_STATEMENT`, `ANNOUNCEMENT`.
- `source_authority`: Axis 1 mapping.
- `review_depth`: Axis 2 mapping.
- `temporal_context`: Axis 3 mapping.
- `claim_status`: One of `UNTESTED`, `SUPPORTED`, `CONTRADICTED`, `UNKNOWN`.
- `support_level`: One of `PHYSICAL_EVIDENCE_VERIFIED`, `SECONDARY_CORROBORATED`, `AUTHORITATIVE_DOC_ALIGNED`, `UNVERIFIED`.
- `evidence_locator`: Abstract URI, content hash, or sanitized reference.

### 3.2 Claim
Propositional statement evaluated against observations:
- `claim_id`: Unique identifier (e.g. `CLM-MIMO-001`).
- `observation_refs`: Array of underlying `observation_id`s.
- `statement`: Propositional claim text.
- `claim_status`: Adjudicated status (`SUPPORTED`, `CONTRADICTED`, `UNTESTED`, `UNKNOWN`).
- `support_level`: Evidence strength tier.
- `confidence`: `LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH`.
- `decay_policy`: Optional parameters defining fact decay, context drift, or expiration windows.

### 3.3 Correction
Append-only revision ledger entry:
- `correction_id`: Unique identifier (e.g. `CORR-001`).
- `target_ref`: Reference to target `Observation`, `Claim`, or `Source`.
- `correction_type`: `PROVENANCE`, `TIMING`, `SEMANTIC`, `AUTHORITY_DOWNGRADE`, `FACTUAL`, `DECAY_INVALIDATION`, `SOURCE_DRIFT`.
- `prior_value`: Value before correction.
- `corrected_value`: Calibrated value.
- `rationale`: Epistemic explanation and audit justification.

### 3.4 Writer Identity & Signature (v0.2, optional)

Two optional Observation fields closing the round-1 dogfood gap (validator covered only
1 of 3 triple members; observations had no writer/signer identity):

- `writer_id` (string, 1–128 chars): identifier of the agent or human that authored the
  observation (e.g. `m`, `grokbot`, `bill`). Optional; **required when `signature` is present**
  (schema `dependentRequired`; validator rule 7 rejects unattributable signatures fail-closed).
- `signature` (string, 128 hex chars): **Ed25519** signature over the canonical serialization
  of the observation **excluding `signature` itself**. Optional.

**Canonicalization (signing input)**: JSON object of all observation fields except `signature`,
keys sorted lexicographically, compact separators (`,` and `:` with no whitespace),
UTF-8 encoded, `ensure_ascii=False`. Deterministic across encoders; any encoder producing
these exact bytes verifies.

**Verification**: `validator.py --verify-sig <PUBKEY_HEX>` verifies present signatures and
fails closed on mismatch (`ERR_SIGNATURE_INVALID`). Without the flag, signatures are ignored
(full backward compatibility: v0.1.0 observations without these fields still PASS).
Signature verification is a soft dependency (`pynacl`); the core fail-closed rules never
require it.

**Key management (pilot scope)**: v0.2 uses explicitly-labeled PILOT experimental keys only.
Production trust-root assignment is a separate governance decision (out of scope for this spec).

---

## 4. Invariant Validation Rules

A compliant validator must enforce the following deterministic invariants (Fail-Closed):

1. **Rule 1: Prohibition of Legacy Conflations**  
   Reject documents containing legacy scalar keys `epistemic_level` or conflated `claim_state`.
2. **Rule 2: Anti-Promotion Guard (Metadata Promoted to Content)**  
   If `review_depth.content_reviewed` is `false`, the record must NOT claim content inspection modalities (`VISUAL_INSPECTION`, `AUDIO_STREAM_PLAYBACK`, `REST_JSON_PAYLOAD`, `STATUS_EVENT_SEQUENCE`) and must NOT claim `support_level: PHYSICAL_EVIDENCE_VERIFIED`.
3. **Rule 3: Authority Ceiling Guard**  
   If `source_authority.type` is `SECONDARY` and `primary_permalink_pinned` is `false`, the record must NOT claim `support_level: PHYSICAL_EVIDENCE_VERIFIED`.
4. **Rule 4: Temporal Decoupling Mandate**  
   `temporal_context.collector_time` is strictly mandatory. At least one temporal anchor (`absolute_event_time` or `relative_source_offset`) must be present.
5. **Rule 5: Clock Skew Calibration Guard**  
   If `abs(clock_skew_seconds) > 60s`, `skew_status` must equal `CALIBRATED_WITH_DISCREPANCY_EXPLAINED`. Marking large skews as uncalibrated `VALID` is rejected.
6. **Rule 6: Composable Modalities**  
   Scalar monolithic labels (e.g. `VIDEO_AUDIO_PLAYBACK`) are forbidden. Modalities must be specified as an explicit list of verified interaction types.
