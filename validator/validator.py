#!/usr/bin/env python3
"""
agent-world-state Candidate Schema Validator (v0.1.0)
Enforces the 3 Orthogonal Epistemic Axes & Prevents Historic Audit Conflations.

Rules Enforced:
1. Orthogonal Separation: review_depth != source_authority != claim_status != support_level != observation_kind.
2. Anti-Promotion Guard: If content_reviewed is false, forbid content inspection modalities and physical verification support.
3. Authority Guard: If source_authority is SECONDARY and unpinned, forbid PHYSICAL_EVIDENCE_VERIFIED support.
4. Temporal Decoupling: collector_time required; at least one of absolute_event_time or relative_source_offset must exist.
5. Clock Skew Integrity: If clock_skew_seconds > 60s, skew_status must be CALIBRATED_WITH_DISCREPANCY_EXPLAINED.
6. Forbidden Legacy Keys: Rejects scalar 'epistemic_level', 'claim_state' (conflated), and monolithic 'VIDEO_AUDIO_PLAYBACK'.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List

VALID_AUTHORITY_TYPES = {"PRIMARY", "MIRROR", "SECONDARY", "LOCAL_BASELINE"}
VALID_OBSERVATION_KINDS = {"ACTION", "STATE_CHANGE", "FAILURE", "INTERVENTION", "RECOVERY", "SPOKEN_STATEMENT", "ANNOUNCEMENT"}
VALID_CLAIM_STATUSES = {"UNTESTED", "SUPPORTED", "CONTRADICTED", "UNKNOWN"}
VALID_SUPPORT_LEVELS = {"PHYSICAL_EVIDENCE_VERIFIED", "SECONDARY_CORROBORATED", "AUTHORITATIVE_DOC_ALIGNED", "UNVERIFIED"}
VALID_MODALITIES = {
    "FRAME_EXTRACTION", "VISUAL_INSPECTION", "BURNED_SUBTITLE_REVIEW",
    "AUDIO_STREAM_PLAYBACK", "REST_JSON_PAYLOAD", "STATUS_EVENT_SEQUENCE",
    "DOM_TEXT_SCRAPE", "SEARCH_QUERY_CORROBORATION"
}
CONTENT_MODALITIES = {"VISUAL_INSPECTION", "AUDIO_STREAM_PLAYBACK", "REST_JSON_PAYLOAD", "STATUS_EVENT_SEQUENCE"}

class ValidationError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

def validate_entry(doc: Dict[str, Any]) -> List[str]:
    errors = []
    
    # Check 1: Forbidden legacy conflated keys
    if "epistemic_level" in doc or "claim_state" in doc:
        errors.append(ValidationError("ERR_CONFLATED_LEGACY_KEYS", 
            "Found legacy conflated keys ('epistemic_level' or 'claim_state'). Must use orthogonal fields: observation_kind, claim_status, support_level.").args[0])
    
    # Check 2: Source Authority
    auth = doc.get("source_authority", {})
    if not isinstance(auth, dict):
        errors.append(ValidationError("ERR_MISSING_AUTHORITY", "source_authority must be a dictionary").args[0])
    else:
        atype = auth.get("type")
        if atype not in VALID_AUTHORITY_TYPES:
            errors.append(ValidationError("ERR_INVALID_AUTHORITY_TYPE", f"Invalid authority type: '{atype}'. Must be one of {sorted(VALID_AUTHORITY_TYPES)}").args[0])

    # Check 3: Review Depth
    rev = doc.get("review_depth", {})
    if not isinstance(rev, dict):
        errors.append(ValidationError("ERR_MISSING_REVIEW_DEPTH", "review_depth must be a dictionary").args[0])
    else:
        content_reviewed = rev.get("content_reviewed", False)
        modalities = rev.get("evidence_modalities", [])
        
        # Check for scalar forbidden enum
        if isinstance(modalities, str) and modalities == "VIDEO_AUDIO_PLAYBACK":
            errors.append(ValidationError("ERR_FORBIDDEN_SCALAR_MODALITY", 
                "Scalar enum 'VIDEO_AUDIO_PLAYBACK' is forbidden. Must use composable list of evidence_modalities.").args[0])
        elif isinstance(modalities, list):
            invalid_m = [m for m in modalities if m not in VALID_MODALITIES]
            if invalid_m:
                errors.append(ValidationError("ERR_INVALID_MODALITY", f"Invalid modalities: {invalid_m}").args[0])
                
            # Rule 2: Anti-Promotion Guard (Metadata promoted to content)
            if not content_reviewed:
                used_content_mod = [m for m in modalities if m in CONTENT_MODALITIES]
                if used_content_mod:
                    errors.append(ValidationError("ERR_METADATA_PROMOTED_TO_CONTENT", 
                        f"content_reviewed is FALSE, but content inspection modalities claimed: {used_content_mod}").args[0])
        else:
            errors.append(ValidationError("ERR_INVALID_MODALITY_FORMAT", "evidence_modalities must be a list").args[0])

    # Check 4: Temporal Decoupling
    temp = doc.get("temporal_context", {})
    if not isinstance(temp, dict):
        errors.append(ValidationError("ERR_MISSING_TEMPORAL_CONTEXT", "temporal_context must be a dictionary").args[0])
    else:
        abs_time = temp.get("absolute_event_time")
        rel_offset = temp.get("relative_source_offset")
        col_time = temp.get("collector_time")
        skew_sec = temp.get("clock_skew_seconds")
        skew_stat = temp.get("skew_status")

        if not col_time:
            errors.append(ValidationError("ERR_MISSING_COLLECTOR_TIME", "collector_time is strictly required").args[0])
        
        if abs_time is None and rel_offset is None:
            errors.append(ValidationError("ERR_TEMPORAL_ANCHOR_MISSING", 
                "Both absolute_event_time and relative_source_offset are missing. At least one temporal anchor is required.").args[0])

        # Rule 5: Clock Skew Integrity
        if skew_sec is not None and abs(skew_sec) > 60:
            if skew_stat != "CALIBRATED_WITH_DISCREPANCY_EXPLAINED":
                errors.append(ValidationError("ERR_UNCALIBRATED_CLOCK_SKEW", 
                    f"Clock skew of {skew_sec}s detected (>60s) without CALIBRATED_WITH_DISCREPANCY_EXPLAINED status (got '{skew_stat}')").args[0])

    # Check 5: Claim & Observation Decomposition
    obs_kind = doc.get("observation_kind")
    if obs_kind not in VALID_OBSERVATION_KINDS:
        errors.append(ValidationError("ERR_INVALID_OBSERVATION_KIND", 
            f"Invalid observation_kind '{obs_kind}'. Must be in {sorted(VALID_OBSERVATION_KINDS)}").args[0])

    claim_stat = doc.get("claim_status")
    if claim_stat not in VALID_CLAIM_STATUSES:
        errors.append(ValidationError("ERR_INVALID_CLAIM_STATUS", 
            f"Invalid claim_status '{claim_stat}'. Must be in {sorted(VALID_CLAIM_STATUSES)}").args[0])

    sup_level = doc.get("support_level")
    if sup_level not in VALID_SUPPORT_LEVELS:
        errors.append(ValidationError("ERR_INVALID_SUPPORT_LEVEL", 
            f"Invalid support_level '{sup_level}'. Must be in {sorted(VALID_SUPPORT_LEVELS)}").args[0])

    # Cross-field Guardrails
    # Guard A: If content_reviewed is False, cannot claim PHYSICAL_EVIDENCE_VERIFIED
    if isinstance(rev, dict) and not rev.get("content_reviewed", False):
        if sup_level == "PHYSICAL_EVIDENCE_VERIFIED":
            errors.append(ValidationError("ERR_CONTENT_UNREVIEWED_PHYSICAL_CLAIM", 
                "Cannot claim support_level: PHYSICAL_EVIDENCE_VERIFIED when content_reviewed is FALSE.").args[0])

    # Guard B: If source is SECONDARY and unpinned, cannot claim PHYSICAL_EVIDENCE_VERIFIED
    if isinstance(auth, dict) and auth.get("type") == "SECONDARY" and not auth.get("primary_permalink_pinned", False):
        if sup_level == "PHYSICAL_EVIDENCE_VERIFIED":
            errors.append(ValidationError("ERR_UNPINNED_SECONDARY_PHYSICAL_CLAIM", 
                "Cannot claim support_level: PHYSICAL_EVIDENCE_VERIFIED for unpinned SECONDARY source.").args[0])

    return errors

def validate_file(filepath: Path) -> bool:
    print(f"--> Validating {filepath.name} ... ", end="")
    try:
        data = yaml.safe_load(filepath.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"FAILED (YAML parse error: {e})")
        return False

    errors = validate_entry(data)
    if not errors:
        print("PASS (Complies with Schema v0.1.0)")
        return True
    else:
        print("FAIL-CLOSED (Errors detected):")
        for err in errors:
            print(f"    - {err}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validator.py <path_to_fixture.yaml> [more_fixtures...]")
        sys.exit(2)

    all_passed = True
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.exists():
            print(f"File not found: {p}")
            all_passed = False
            continue
        if not validate_file(p):
            all_passed = False

    sys.exit(0 if all_passed else 1)
