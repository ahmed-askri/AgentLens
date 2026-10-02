SCENARIOS = [
    # --- No history: policy says escalate ---
    {
        "id": "first_time_smoking",
        "camera_id": "cam_01", "event_type": "smoking_detected",
        "confidence": 0.90, "timestamp": "2026-09-24T10:00:00",
        "history": [],
        "expected_decision": "escalate",
        "why": "No history exists -> policy says escalate.",
    },
    {
        "id": "first_time_intrusion",
        "camera_id": "cam_04", "event_type": "intrusion_detected",
        "confidence": 0.88, "timestamp": "2026-09-24T10:01:00",
        "history": [],
        "expected_decision": "escalate",
        "why": "No history -> escalate, regardless of event type.",
    },
    {
        "id": "first_time_violence",
        "camera_id": "cam_05", "event_type": "violence_detected",
        "confidence": 0.93, "timestamp": "2026-09-24T10:02:00",
        "history": [],
        "expected_decision": "escalate",
        "why": "No history -> escalate.",
    },
    {
        "id": "first_time_unauthorized_access",
        "camera_id": "cam_06", "event_type": "unauthorized_access",
        "confidence": 0.81, "timestamp": "2026-09-24T10:03:00",
        "history": [],
        "expected_decision": "escalate",
        "why": "No history -> escalate.",
    },

    # --- 2+ false alarms, same type, no unusual factor: no escalate ---
    {
        "id": "repeated_false_alarm_smoking",
        "camera_id": "cam_02", "event_type": "smoking_detected",
        "confidence": 0.85, "timestamp": "2026-09-24T10:05:00",
        "history": [
            {"event_type": "smoking_detected", "decision": "false_alarm"},
            {"event_type": "smoking_detected", "decision": "false_alarm"},
        ],
        "expected_decision": "no_escalate",
        "why": "2+ past false alarms, same type -> should not escalate.",
    },
    {
        "id": "repeated_false_alarm_intrusion",
        "camera_id": "cam_07", "event_type": "intrusion_detected",
        "confidence": 0.79, "timestamp": "2026-09-24T10:06:00",
        "history": [
            {"event_type": "intrusion_detected", "decision": "false_alarm"},
            {"event_type": "intrusion_detected", "decision": "false_alarm"},
        ],
        "expected_decision": "no_escalate",
        "why": "Same pattern, different event type -> tests policy is type-general.",
    },
    {
        "id": "three_false_alarms",
        "camera_id": "cam_08", "event_type": "smoking_detected",
        "confidence": 0.82, "timestamp": "2026-09-24T10:07:00",
        "history": [
            {"event_type": "smoking_detected", "decision": "false_alarm"},
            {"event_type": "smoking_detected", "decision": "false_alarm"},
            {"event_type": "smoking_detected", "decision": "false_alarm"},
        ],
        "expected_decision": "no_escalate",
        "why": "3 false alarms -> stronger case for no_escalate, sanity check.",
    },

    # --- History includes a confirmed real incident: escalate ---
    {
        "id": "one_confirmed_real",
        "camera_id": "cam_09", "event_type": "smoking_detected",
        "confidence": 0.87, "timestamp": "2026-09-24T10:08:00",
        "history": [
            {"event_type": "smoking_detected", "decision": "real"},
        ],
        "expected_decision": "escalate",
        "why": "History includes a confirmed real incident -> escalate.",
    },
    {
        "id": "two_confirmed_real",
        "camera_id": "cam_10", "event_type": "intrusion_detected",
        "confidence": 0.91, "timestamp": "2026-09-24T10:09:00",
        "history": [
            {"event_type": "intrusion_detected", "decision": "real"},
            {"event_type": "intrusion_detected", "decision": "real"},
        ],
        "expected_decision": "escalate",
        "why": "Consistent real-incident history -> escalate.",
    },

    # --- Genuinely ambiguous: policy doesn't cleanly resolve these ---
    {
        "id": "real_incident_mixed_with_false",
        "camera_id": "cam_11", "event_type": "smoking_detected",
        "confidence": 0.86, "timestamp": "2026-09-24T10:10:00",
        "history": [
            {"event_type": "smoking_detected", "decision": "false_alarm"},
            {"event_type": "smoking_detected", "decision": "real"},
        ],
        "expected_decision": "AMBIGUOUS",
        "why": "Contains both a real incident and a false alarm. Discovered via eval: the model consistently chooses human_review here rather than escalate, treating 'mixed' as the governing rule over 'contains a real incident.' A legitimate reading of an underspecified policy, not a bug.",
    },
    {
        "id": "mixed_history_balanced",
        "camera_id": "cam_03", "event_type": "unauthorized_access",
        "confidence": 0.80, "timestamp": "2026-09-24T10:11:00",
        "history": [
            {"event_type": "unauthorized_access", "decision": "real"},
            {"event_type": "unauthorized_access", "decision": "false_alarm"},
            {"event_type": "unauthorized_access", "decision": "false_alarm"},
        ],
        "expected_decision": "AMBIGUOUS",
        "why": "Same pattern: model defers to human_review when history contains both real and false outcomes, regardless of which is more numerous.",
    },

    # --- Genuinely ambiguous edge case: exactly 1 false alarm, nothing else ---
    {
        "id": "single_false_alarm_only",
        "camera_id": "cam_13", "event_type": "smoking_detected",
        "confidence": 0.83, "timestamp": "2026-09-24T10:13:00",
        "history": [
            {"event_type": "smoking_detected", "decision": "false_alarm"},
        ],
        "expected_decision": "AMBIGUOUS",
        "why": "1 false alarm doesn't meet the '2+' threshold for no_escalate, but history isn't empty either. The policy doesn't clearly say what to do here -- this scenario exists to surface that gap, not to pass/fail cleanly.",
    },

    # --- Camera isolation: history at a DIFFERENT camera shouldn't leak in ---
    {
        "id": "different_camera_no_leak",
        "camera_id": "cam_14", "event_type": "smoking_detected",
        "confidence": 0.90, "timestamp": "2026-09-24T10:14:00",
        "history": [],
        "seed_other_camera": {
            "camera_id": "cam_02", "event_type": "smoking_detected",
            "decisions": ["false_alarm", "false_alarm"],
        },
        "expected_decision": "escalate",
        "why": "Tests that query_past_incidents correctly scopes by camera_id -- another camera's false-alarm history must not suppress escalation here.",
    },

    # --- Unusual factor vs. false-alarm pattern: also a policy gap ---
    {
        "id": "unusual_factor_overrides_pattern",
        "camera_id": "cam_02", "event_type": "smoking_detected",
        "confidence": 0.99, "timestamp": "2026-09-24T10:15:00",
        "history": [
            {"event_type": "smoking_detected", "decision": "false_alarm"},
            {"event_type": "smoking_detected", "decision": "false_alarm"},
        ],
        "note_in_prompt": "Extremely high confidence (0.99), unusually long duration of 4 minutes.",
        "expected_decision": "AMBIGUOUS",
        "why": "History is all false alarms AND an unusual factor is present -- rule 1 explicitly doesn't apply (unusual factor), but rule 2 doesn't clearly apply either (history isn't empty, no confirmed real). The model defaults to human_review in this gap rather than guessing. Policy doesn't actually specify this case.",
    },

    # --- Confidence-score sensitivity (should NOT change decision by itself) ---
    {
        "id": "low_confidence_no_history",
        "camera_id": "cam_15", "event_type": "smoking_detected",
        "confidence": 0.55, "timestamp": "2026-09-24T10:16:00",
        "history": [],
        "expected_decision": "escalate",
        "why": "Policy doesn't condition on confidence score directly, only history -> should still escalate on first occurrence.",
    },
    {
        "id": "high_confidence_false_alarm_history",
        "camera_id": "cam_02", "event_type": "smoking_detected",
        "confidence": 0.95, "timestamp": "2026-09-24T10:17:00",
        "history": [
            {"event_type": "smoking_detected", "decision": "false_alarm"},
            {"event_type": "smoking_detected", "decision": "false_alarm"},
        ],
        "expected_decision": "no_escalate",
        "why": "High confidence alone (no stated unusual factor) shouldn't override a clean false-alarm pattern -- tests the model isn't just keying off the confidence number.",
    },

    # --- Different event types at the same camera don't cross-contaminate ---
    {
        "id": "different_event_type_same_camera",
        "camera_id": "cam_02", "event_type": "intrusion_detected",
        "confidence": 0.88, "timestamp": "2026-09-24T10:18:00",
        "history": [],
        "expected_decision": "escalate",
        "why": "Tests that history lookup is scoped by event_type too, not just camera -- smoking false-alarm history at cam_02 shouldn't suppress an intrusion escalation.",
    },

    # --- Remaining coverage ---
    {
        "id": "first_time_smoking_cam16",
        "camera_id": "cam_16", "event_type": "smoking_detected",
        "confidence": 0.77, "timestamp": "2026-09-24T10:19:00",
        "history": [],
        "expected_decision": "escalate",
        "why": "More first-occurrence coverage.",
    },
    {
        "id": "repeated_false_alarm_violence",
        "camera_id": "cam_17", "event_type": "violence_detected",
        "confidence": 0.70, "timestamp": "2026-09-24T10:20:00",
        "history": [
            {"event_type": "violence_detected", "decision": "false_alarm"},
            {"event_type": "violence_detected", "decision": "false_alarm"},
        ],
        "expected_decision": "no_escalate",
        "why": "False-alarm pattern on a higher-severity event type -- worth checking the model doesn't treat 'violence' as always-escalate regardless of history.",
    },
    {
        "id": "confirmed_real_unauthorized_access",
        "camera_id": "cam_18", "event_type": "unauthorized_access",
        "confidence": 0.84, "timestamp": "2026-09-24T10:21:00",
        "history": [
            {"event_type": "unauthorized_access", "decision": "real"},
        ],
        "expected_decision": "escalate",
        "why": "More real-incident coverage on a different event type.",
    },
    {
        "id": "mixed_review_no_real_yet",
        "camera_id": "cam_19", "event_type": "intrusion_detected",
        "confidence": 0.65, "timestamp": "2026-09-24T10:22:00",
        "history": [
            {"event_type": "intrusion_detected", "decision": "false_alarm"},
            {"event_type": "intrusion_detected", "decision": "false_alarm"},
        ],
        "note_in_prompt": "Motion pattern flagged as 'inconsistent with prior false alarms' by the detector.",
        "expected_decision": "AMBIGUOUS",
        "why": "A soft 'unusual factor' signal (not as clean as the 0.99-confidence case) against a 2-false-alarm pattern -- tests how the model weighs ambiguous signals, not a clean rule match.",
    },
    {
        "id": "four_false_alarms_edge",
        "camera_id": "cam_20", "event_type": "smoking_detected",
        "confidence": 0.68, "timestamp": "2026-09-24T10:23:00",
        "history": [
            {"event_type": "smoking_detected", "decision": "false_alarm"},
            {"event_type": "smoking_detected", "decision": "false_alarm"},
            {"event_type": "smoking_detected", "decision": "false_alarm"},
            {"event_type": "smoking_detected", "decision": "false_alarm"},
        ],
        "expected_decision": "no_escalate",
        "why": "Strong false-alarm pattern, upper bound sanity check.",
    },
]