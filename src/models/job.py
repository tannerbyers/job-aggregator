from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class RemoteType(str, Enum):
    REMOTE_US = "remote_us"
    REMOTE_OTHER = "remote_other"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    UNKNOWN = "unknown"


class Job(BaseModel):
    job_id: str
    external_id: Optional[str] = None
    company: str
    ticker: Optional[str] = None
    title: str
    department: Optional[str] = None
    location: str
    remote_type: RemoteType = RemoteType.UNKNOWN
    employment_type: EmploymentType = EmploymentType.UNKNOWN
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    description: Optional[str] = None
    apply_url: str
    source: str
    posted_at: Optional[datetime] = None
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    score: int = 0
    score_reasons: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)

    def to_digest_string(self) -> str:
        salary = ""
        if self.salary_min and self.salary_max:
            salary = f"${self.salary_min:,}-${self.salary_max:,}"
        elif self.salary_min:
            salary = f"${self.salary_min:,}+"
        return f"{self.title} at {self.company} | {self.location} | {salary} | Score: {self.score}"
