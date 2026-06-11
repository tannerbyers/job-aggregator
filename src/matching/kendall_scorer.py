from datetime import datetime
from typing import Optional, Tuple

from src.models.job import Job


KENDALL_DOMAINS_BOOST = [
    "revenue cycle", "claims", "clearinghouse", "payer connectivity",
    "provider connectivity", "edi", "837", "835", "276", "277", "278",
    "remittance", "eligibility", "authorization", "claim status",
    "payment accuracy", "payment integrity", "hipaa", "cms",
    "uat", "qa", "roadmap", "product discovery", "backlog",
    "release cycle", "vendor evaluation", "stakeholders",
    "real world data", "rwd", "clinical data", "health data",
    "value based care", "population health",
]

KENDALL_DOMAINS_PENALIZE = [
    "project manager", "scrum master", "sales", "marketing",
    "customer success", "engineering", "developer", "data science",
]

SENIORITY_PENALTIES = {
    "senior": -5,
    "lead": -5,
    "principal": -10,
    "group": -10,
    "head": -15,
}

PM_TITLE_KEYWORDS = ["product manager", "product owner", "program manager"]
PM_ADJACENT_KEYWORDS = ["analyst"]
PM_EXCLUDE_KEYWORDS = ["sales", "marketing", "customer success", "implementation", "support", "training", "solutions", "technical qa", "qa analyst", "quality assurance", "tester"]


def hard_reject(job: Job, include_contract: bool = True) -> Tuple[bool, str]:
    title_lower = job.title.lower()
    location_lower = job.location.lower()

    if job.remote_type.value == "hybrid":
        return True, "Hybrid role"
    if job.remote_type.value == "onsite":
        return True, "Onsite role"
    if job.remote_type.value == "remote_other":
        return True, "Not US remote"

    if any(t in title_lower for t in ["vp ", "vice president", " vP", "vp,"]):
        return True, "VP level"
    if any(t in title_lower for t in ["director", "senior director"]):
        return True, "Director level"
    if any(t in title_lower for t in ["principal ", "principal,"]):
        return True, "Principal level"
    if any(t in title_lower for t in ["staff "]):
        return True, "Staff level"

    if any(t in title_lower for t in ["sales", "account executive", "AE ", "customer success"]):
        return True, "Sales/customer success"
    if any(t in title_lower for t in ["marketing manager", "marketing director"]):
        return True, "Marketing role"
    if any(t in title_lower for t in ["nurse", "physician", "doctor", "pharmacist", "rph"]):
        return True, "Clinical role"
    if any(t in title_lower for t in ["medical assistant"]):
        return True, "Clinical role"
    if any(t in title_lower for t in ["utilization management", "appeals technician", "prior auth"]):
        return True, "Operations role"
    billing_only = any(t in title_lower for t in ["billing specialist", "billing coordinator", "billing associate", "billing clerk"])
    if "billing" in title_lower and not any(t in title_lower for t in ["rcm", "revenue cycle", "revenue management"]):
        return True, "Billing role"

    if any(t in title_lower for t in ["engineering manager", "engineering lead", "tech lead"]):
        return True, "Engineering role"
    if any(t in title_lower for t in ["software engineer", "developer", "data scientist"]):
        return True, "Engineering role"
    if any(t in title_lower for t in ["solutions engineer", "solutions architect", "pre-sales"]):
        return True, "Solutions/pre-sales role"

    if not include_contract and "contract" in title_lower:
        return True, "Contract only"

    return False, ""


def score_kendall(job: Job, profile: dict, adjustments: dict = None) -> Tuple[int, list[str], list[str]]:
    score = 0
    reasons = []
    risks = []

    if adjustments is None:
        adjustments = {}

    domain_boosts = adjustments.get("domain_boosts", {})
    seniority_penalties = adjustments.get("seniority_penalties", SENIORITY_PENALTIES)
    company_penalties = adjustments.get("company_penalties", [])

    if job.remote_type.value == "remote_us":
        score += 30
        reasons.append("Remote US")

    if job.posted_at:
        days_since = (datetime.utcnow() - job.posted_at.replace(tzinfo=None)).days
        if days_since <= 3:
            score += 20
            reasons.append(f"Fresh ({days_since}d ago)")
        elif days_since > 30:
            score -= 20
            risks.append("Posted >30 days ago")

    title_lower = job.title.lower()
    preferred_titles = profile.get("preferred_titles", [])
    is_pm_title = any(pm_kw in title_lower for pm_kw in PM_TITLE_KEYWORDS)
    is_pm_adjacent = any(pm_kw in title_lower for pm_kw in PM_ADJACENT_KEYWORDS)
    is_pm_excluded = any(pm_kw in title_lower for pm_kw in PM_EXCLUDE_KEYWORDS)

    desc_lower = (job.description or "")[:2000].lower()
    title_desc = title_lower + " " + desc_lower

    domain_matches = []
    for domain in KENDALL_DOMAINS_BOOST:
        if domain in title_desc:
            domain_matches.append(domain)
            boost_key = domain.replace(" ", "_").replace("-", "_")
            score += domain_boosts.get(boost_key, 8)

    if domain_matches:
        reasons.append(f"Domain: {', '.join(domain_matches[:2])}")

    if any(job.title.lower() == t.lower() for t in preferred_titles):
        score += 25
        reasons.append("Exact preferred title")
    elif is_pm_title:
        score += 20
        reasons.append("PM title match")
    elif is_pm_adjacent and not is_pm_excluded and domain_matches:
        score += 5
        reasons.append("PM-adjacent role (analyst + domain)")
    elif is_pm_excluded:
        score -= 10
        risks.append("Non-PM role (sales/implement/support)")

    company_lower = job.company.lower()
    healthcare_name_patterns = ["inovalon", "cohere", "mcg", "qgenda", "tebra", "elation", "luma", "advancedmd", "komodo", "healthverity", "capital"]
    is_healthcare_company = any(kw in company_lower for kw in ["health", "healthcare", "medical", "payer", "provider", "insurance", "rx", "rcm", "clearinghouse"]) or any(p in company_lower for p in healthcare_name_patterns)

    if is_healthcare_company:
        score += 25
        reasons.append("Healthcare company")
        if is_pm_title:
            score += 15
            reasons.append("PM role at healthcare company")

    penalty_domains = adjustments.get("domain_penalties", {})
    for domain in KENDALL_DOMAINS_PENALIZE:
        if domain in title_lower:
            score -= 15
            risks.append(f"Generic role: {domain}")

    if job.company.lower() in [c.lower() for c in company_penalties]:
        score -= 15
        risks.append("Previously skipped company")

    for seniority, penalty in seniority_penalties.items():
        if seniority in title_lower:
            score += penalty
            break

    if " sql" in title_lower or "python" in title_lower or "coding" in title_lower:
        risks.append("May require coding")

    if job.salary_min and job.salary_max:
        score += 5
        reasons.append("Salary visible")

    return score, reasons, risks
