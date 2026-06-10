from datetime import datetime, timedelta
from typing import Optional

from src.models.job import Job
from src.models.candidate import CandidateConfig


SCORING_RULES = {
    "remote_us": 40,
    "exact_title_match": 30,
    "product_adjacent_title": 20,
    "salary_visible": 15,
    "recently_posted": 10,
    "preferred_industry": 10,
    "remote_friendly_company": 10,
    "sp500_company": 5,
    "hybrid": -30,
    "wrong_country": -40,
    "unclear_remote": -25,
    "too_senior": -20,
    "wrong_function": -20,
}


class JobScorer:
    def __init__(self, config: CandidateConfig):
        self.config = config
        self.target_titles_lower = [t.lower() for t in config.target_titles]

    def score(self, job: Job) -> tuple[int, list[str]]:
        score = 0
        reasons = []

        if job.remote_type.value == "remote_us":
            score += SCORING_RULES["remote_us"]
            reasons.append("Remote US")

        title_lower = job.title.lower()
        title_words = set(title_lower.replace("-", " ").replace("/", " ").split())

        exact_match = any(job.title.lower() == t.lower() for t in self.config.target_titles)

        core_pm_keywords = [
            "product manager", "product owner", "technical product manager",
            "project manager", "program manager", "delivery manager",
            "agile project manager", "agile delivery manager", "scrum master",
            "product operations manager", "product analyst", "business analyst",
        ]
        core_pm_match = any(kw in title_lower for kw in core_pm_keywords)

        prefix_match = any(
            title_lower.startswith(t.lower() + " ") or
            title_lower.startswith(t.lower() + " - ") or
            title_lower.startswith(t.lower() + ",")
            for t in ["product manager", "product owner", "technical product manager"]
        )

        if exact_match:
            score += SCORING_RULES["exact_title_match"]
            reasons.append(f"Exact title match: {job.title}")
        elif prefix_match:
            score += SCORING_RULES["exact_title_match"]
            reasons.append(f"Exact title prefix: {job.title}")
        elif core_pm_match:
            score += SCORING_RULES["product_adjacent_title"]
            reasons.append("Product-adjacent title match")

        if job.salary_min and job.salary_max:
            score += SCORING_RULES["salary_visible"]
            reasons.append("Salary visible")

        if job.posted_at:
            days_since_posted = (datetime.utcnow() - job.posted_at.replace(tzinfo=None)).days
            if days_since_posted <= 7:
                score += SCORING_RULES["recently_posted"]
                reasons.append("Recently posted (within 7 days)")

        for industry in self.config.preferred_industries:
            if industry.lower() in job.company.lower():
                score += SCORING_RULES["preferred_industry"]
                reasons.append(f"Preferred industry: {industry}")
                break

        return score, reasons

    def is_minimum_score(self, job: Job, threshold: int = 70) -> bool:
        score, _ = self.score(job)
        return score >= threshold
