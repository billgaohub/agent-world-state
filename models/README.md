# agent-world-state Data Models & Architecture

## Overview

The `agent-world-state` data model defines the structures required to track external real-world telemetry, multi-agent sensor inputs, and causal verification loops without contaminating internal agent cognitive memory.

## Core Relational Graph

```
[ Source ] (Authority Standing & Review Depth)
    |
    v (produces)
[ Observation ] (Atomic Grounded Fact, Temporal Context)
    |
    +---> [ Claim ] (Propositional Synthesis & Decay Policy)
    |         |
    |         v (evaluates)
    |     [ Claim Status ] (SUPPORTED / CONTRADICTED / UNTESTED)
    |
    +---> [ CausalSequence ] (Failure -> Intervention -> Recovery)
    |
    v (on drift / skew / revision)
[ Correction ] (Immutable Revision Ledger Record)
```

## Entity Reference

### 1. Source (`schemas/source.schema.json`)
Represents the origin sensor, stream, API, or mirror transmitting reality signals.
- **Authority Type**: `PRIMARY`, `MIRROR`, `SECONDARY`, `LOCAL_BASELINE`.
- **Review Depth**: `identity_pinned`, `metadata_verified`, `content_reviewed`, `evidence_modalities`.

### 2. Temporal Context (`schemas/temporal-context.schema.json`)
Decouples timeline dimensions to prevent observer clock skew from corrupting historical causality:
- `absolute_event_time`: Event origin epoch (ISO 8601 UTC).
- `relative_source_offset`: Stream or step offset (e.g. `T+00:48:30`, `step: 15`).
- `collector_time`: Wall clock of the observing agent execution (mandatory).
- `published_or_observed_clock`: Display timestamp shown on external dashboards.
- `clock_skew_seconds` & `skew_status`: Quantified drift and verification state.

### 3. Observation (`schemas/observation.schema.json`)
The immutable atomic unit of physical telemetry:
- `observation_id`: Unique identifier (e.g., `OBS-GROKBOT-008`).
- `observation_kind`: `ACTION`, `STATE_CHANGE`, `FAILURE`, `INTERVENTION`, `RECOVERY`, `SPOKEN_STATEMENT`, `ANNOUNCEMENT`.
- `support_level`: `PHYSICAL_EVIDENCE_VERIFIED`, `SECONDARY_CORROBORATED`, `AUTHORITATIVE_DOC_ALIGNED`, `UNVERIFIED`.

### 4. Claim (`schemas/claim.schema.json`)
Propositional statements synthesized from observations. Unlike raw observations, claims are subject to decay:
- `claim_status`: `UNTESTED`, `SUPPORTED`, `CONTRADICTED`, `UNKNOWN`.
- `decay_policy`: Governs how contextual shift, fact decay, or coverage expiration affects claim validity over time.

### 5. Correction (`schemas/correction.schema.json`)
When external sources update, stream offsets are calibrated, or stale claims drift, prior records are **never mutated silently**. An immutable `Correction` record is appended:
- `correction_type`: `PROVENANCE`, `TIMING`, `SEMANTIC`, `AUTHORITY_DOWNGRADE`, `FACTUAL`, `DECAY_INVALIDATION`, `SOURCE_DRIFT`.
- `prior_value` vs `corrected_value` + `rationale`.
