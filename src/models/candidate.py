from typing import Optional
from pydantic import BaseModel, Field


class CandidateConfig(BaseModel):
    location: str = "North Carolina"
    remote_required: bool = True
    country: str = "US"
    min_salary: Optional[int] = 100000

    target_titles: list[str] = [
        "Product Owner",
        "Product Manager",
        "Technical Product Manager",
        "Project Manager",
        "Program Manager",
        "Delivery Manager",
        "Agile Project Manager",
        "Agile Delivery Manager",
        "Scrum Master",
        "Product Operations Manager",
        "Product Analyst",
        "Business Analyst",
    ]

    preferred_industries: list[str] = [
        "SaaS",
        "Healthcare",
        "Fintech",
        "B2B",
        "Internal Tools",
        "Cloud",
    ]

    excluded_titles: list[str] = [
        "intern",
        "student",
        "vp",
        "vice president",
        "director",
        "senior director",
        "principal",
        "staff",
        "engineering manager",
        "sales",
        "account executive",
        "marketing manager",
        "hardware",
        "mechanical",
        "warehouse",
        "retail",
    ]

    include_title_keywords: list[str] = [
        "product owner",
        "product manager",
        "technical product manager",
        "project manager",
        "program manager",
        "delivery manager",
        "agile project manager",
        "agile delivery manager",
        "scrum master",
        "product operations",
        "product analyst",
        "business analyst",
    ]

    remote_include_keywords: list[str] = [
        "remote",
        "remote - us",
        "remote united states",
        "work from home",
        "anywhere in the united states",
        "distributed",
    ]

    remote_exclude_keywords: list[str] = [
        "hybrid",
        "onsite",
        "on-site",
        "must be located in",
        "remote canada",
        "remote europe",
        "remote uk",
    ]
