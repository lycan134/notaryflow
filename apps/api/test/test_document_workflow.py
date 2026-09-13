from app.services.document_workflow import (
    validate_document_status_transition,
)


def test_uploaded_can_transition_to_under_review():
    assert validate_document_status_transition(
        "UPLOADED",
        "UNDER_REVIEW",
    ) is True


def test_under_review_can_transition_to_reviewed():
    assert validate_document_status_transition(
        "UNDER_REVIEW",
        "REVIEWED",
    ) is True


def test_under_review_can_transition_to_rejected():
    assert validate_document_status_transition(
        "UNDER_REVIEW",
        "REJECTED",
    ) is True


def test_rejected_can_transition_to_under_review():
    assert validate_document_status_transition(
        "REJECTED",
        "UNDER_REVIEW",
    ) is True


def test_reviewed_cannot_transition_to_any_status():
    assert validate_document_status_transition(
        "REVIEWED",
        "UPLOADED",
    ) is False

    assert validate_document_status_transition(
        "REVIEWED",
        "UNDER_REVIEW",
    ) is False

    assert validate_document_status_transition(
        "REVIEWED",
        "REJECTED",
    ) is False


def test_invalid_transitions_are_rejected():
    assert validate_document_status_transition(
        "UPLOADED",
        "REVIEWED",
    ) is False

    assert validate_document_status_transition(
        "UPLOADED",
        "REJECTED",
    ) is False

    assert validate_document_status_transition(
        "REJECTED",
        "REVIEWED",
    ) is False


def test_unknown_status_is_rejected():
    assert validate_document_status_transition(
        "UNKNOWN",
        "UNDER_REVIEW",
    ) is False