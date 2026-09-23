class PrivacyViolationError(Exception):
    pass

def verify_k_anonymity(cohort_size: int, k_threshold: int = 5) -> None:
    if cohort_size < k_threshold:
        raise PrivacyViolationError(
            f"Privacy Violation: Cohort size ({cohort_size}) is below k-anonymity threshold (k={k_threshold})."
        )
