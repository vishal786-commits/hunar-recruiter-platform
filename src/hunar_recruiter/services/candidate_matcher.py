from __future__ import annotations

import re

from hunar_recruiter.models.candidate import Candidate


def normalize_text(value: str | None) -> str:
    if not value:
        return ""

    value = value.lower()
    value = re.sub(r"[^a-z0-9+#.]", " ", value)

    return value


def calculate_match_score(
    candidate: Candidate,
    job,
) -> float:
    """
    Simple deterministic candidate/JD matcher.

    Score:
    - Required skills: 70%
    - Preferred skills: 20%
    - Title relevance: 10%
    """

    required_skills = job.skills.required or []
    preferred_skills = job.skills.preferred or []

    candidate_skills = {
        normalize_text(skill)
        for skill in candidate.skills
    }

    required = {
        normalize_text(skill)
        for skill in required_skills
    }

    preferred = {
        normalize_text(skill)
        for skill in preferred_skills
    }

    score = 0.0

    # Required skills
    if required:
        matched_required = required.intersection(candidate_skills)

        score += (
            len(matched_required) / len(required)
        ) * 70

    # Preferred skills
    if preferred:
        matched_preferred = preferred.intersection(candidate_skills)

        score += (
            len(matched_preferred) / len(preferred)
        ) * 20

    # Job-title relevance
    job_title = normalize_text(job.title)
    candidate_title = normalize_text(candidate.current_title)

    if job_title and candidate_title:
        job_words = set(job_title.split())
        candidate_words = set(candidate_title.split())

        if job_words.intersection(candidate_words):
            score += 10

    return round(min(score, 100), 2)