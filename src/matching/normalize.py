import re
from typing import Optional

from src.models.job import Job, RemoteType, EmploymentType


def normalize_company_name(company: str) -> str:
    suffixes = [
        r",?\s*Inc\.?$",
        r",?\s*LLC\.?$",
        r",?\s*Ltd\.?$",
        r",?\s*Corp\.?$",
        r",?\s*Co\.?$",
        r",?\s*LLP\.?$",
    ]
    normalized = company.strip()
    for suffix in suffixes:
        normalized = re.sub(suffix, "", normalized, flags=re.IGNORECASE)
    return normalized.strip().lower()


def normalize_title(title: str) -> str:
    return title.strip().lower()


def normalize_location(location: str) -> str:
    return location.strip().lower()


def generate_job_id(company: str, title: str, location: str, url: str) -> str:
    import hashlib
    raw = f"{normalize_company_name(company)}-{normalize_title(title)}-{normalize_location(location)}-{url}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def normalize_job(raw_job: dict, source: str) -> Job:
    job = Job(
        job_id=generate_job_id(
            raw_job.get("company", ""),
            raw_job.get("title", ""),
            raw_job.get("location", ""),
            raw_job.get("apply_url", ""),
        ),
        external_id=raw_job.get("id") or raw_job.get("external_id"),
        company=raw_job.get("company", "Unknown"),
        title=raw_job.get("title", ""),
        department=raw_job.get("department"),
        location=raw_job.get("location", "Unknown"),
        remote_type=raw_job.get("remote_type", RemoteType.UNKNOWN),
        employment_type=raw_job.get("employment_type", EmploymentType.UNKNOWN),
        salary_min=raw_job.get("salary_min"),
        salary_max=raw_job.get("salary_max"),
        salary_currency=raw_job.get("salary_currency", "USD"),
        description=raw_job.get("description"),
        apply_url=raw_job.get("apply_url", ""),
        source=source,
        posted_at=raw_job.get("posted_at"),
    )
    return job
