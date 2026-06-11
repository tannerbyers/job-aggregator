# Research Agent - Complete Source Reference

## File Locations

| File | Purpose |
|------|---------|
| `data/source_registry.json` | Active company sources |
| `src/models/candidate.py` | Candidate preferences (titles, keywords) |
| `src/matching/scoring.py` | Scoring rules |
| `healthcare-companies.txt` | Full list of target healthcare companies |
| `healthcare-titles.txt` | Healthcare-specific job titles |

---

## Greenhouse API

**Endpoint:** `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`

**Test Script:**
```python
import requests
url = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
r = requests.get(url, timeout=10)
jobs = r.json().get("jobs", [])
print(f"Company: {len(jobs)} jobs")
```

---

## Lever API

**Endpoint:** `https://api.lever.co/v0/postings/{slug}?mode=json`

**Test Script:**
```python
import requests
url = "https://api.lever.co/v0/postings/{slug}?mode=json"
r = requests.get(url, timeout=10)
data = r.json()
if isinstance(data, list):
    print(f"Company: {len(data)} jobs")
```

---

## Ashby API

**Endpoint:** `https://api.ashbyhq.com/posting-api/job-board/{slug}`

**Test Script:**
```python
import requests
url = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
r = requests.get(url, timeout=10)
print(r.json())
```

---

## SmartRecruiters API

**Endpoint:** `https://api.smartrecruiters.com/public/v1/companies/{slug}/jobs`

**Test Script:**
```python
import requests
url = "https://api.smartrecruiters.com/public/v1/companies/{slug}/jobs"
r = requests.get(url, timeout=10)
print(r.json())
```

---

## RemoteOK API

**Endpoint:** `https://remoteok.com/api`

**Headers:** `{"User-Agent": "Job Aggregator/1.0"}`

**Response Format:** Array with first item being metadata
```python
import requests
url = "https://remoteok.com/api"
headers = {"User-Agent": "Job Aggregator/1.0"}
r = requests.get(url, headers=headers, timeout=30)
data = r.json()  # First item is metadata, rest are jobs
```

---

## Job Title Keywords to Match

From `src/models/candidate.py`:

**Exact Match Targets:**
- Product Owner, Product Manager, Technical Product Manager
- Project Manager, Program Manager, Delivery Manager
- Agile Project Manager, Agile Delivery Manager
- Scrum Master, Product Operations Manager
- Product Analyst, Business Analyst
- Healthcare Product Manager, Claims Product Manager
- Revenue Cycle Product Manager, Prior Authorization Product Manager
- Interoperability Product Manager, FHIR Product Manager
- EDI Product Manager, Payer Platform Product Manager
- Provider Portal Product Manager, Healthcare Data Product Manager

**Partial Match Keywords:**
- product owner, product manager, technical product manager
- project manager, program manager, delivery manager
- agile project manager, agile delivery manager, scrum master
- product operations, product analyst, business analyst
- claims product, revenue cycle product, prior auth
- interoperability, fhir product, edi product
- payer platform, provider portal, healthcare data

---

## Scoring Rules

From `src/matching/scoring.py`:

```python
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
    "healthcare_boost": 25,
    "healthcare_title": 15,
}
```

---

## Healthcare Keywords for Boost

```python
HEALTHCARE_KEYWORDS = [
    "healthcare", "health care", "health", "medical", "medicine", "hospital",
    "clinic", "patient", "clinical", "pharma", "pharmaceutical", "biotech",
    "biotechnology", "life sciences", "health tech",
    "ehr", "emr", "electronic health", "electronic medical",
    "insurance", "payer", "provider", "benefits", "hmo", "ppo",
    "telemedicine", "telehealth", "remote patient", "virtual care",
]
```

---

## Remote Detection Rules

**Include:**
- remote, remote - us, remote united states
- work from home, anywhere in the united states, distributed

**Exclude:**
- hybrid, onsite, on-site
- must be located in
- remote canada, remote europe, remote uk

**Non-US Locations (flag as REMOTE_OTHER):**
```
canada, europe, uk, united kingdom, germany, france, ireland,
netherlands, spain, italy, sweden, norway, denmark, finland,
poland, czech, hungary, romania, bulgaria, ukraine, russia,
australia, new zealand, singapore, japan, china, india, brazil,
mexico, argentina, chile, colombia, uae, dubai, israel,
south africa, kenya, egypt, nigeria, hong kong, malaysia,
thailand, indonesia, philippines
```

---

## Company Discovery Approach

### Method 1: Greenhouse Slug Probing
Generate slugs from company name and probe:
- waystar → waystar
- Inovalon → inovalon
- "The Walt Disney Company" → disney, waltdisney, disneycorp

### Method 2: ATS Domain Detection
Fetch company homepage and look for:
- greenhouse.io
- lever.co
- ashbyhq.com
- smartrecruiters.com
- myworkdayjobs.com
- icims.com
- workable.com
- jobvite.com
- successfactors.com

### Method 3: Career Page Inspection
Check `/careers`, `/jobs`, `/careers/all-jobs` paths

---

## Priority Companies to Research First

Based on healthcare-companies.txt "Best" and "Strong" fit ratings:

**Highest Priority (RCM/Claims/Payments):**
1. Waystar
2. Zelis
3. FinThrive
4. Experian Health
5. Edifecs
6. Cognizant TriZetto
7. HealthEdge
8. Cotiviti
9. MultiPlan
10. R1 RCM
11. Ensemble Health Partners

**High Priority (Value-Based Care):**
12. Optum Insight
13. Change Healthcare
14. Evolent Health
15. Carelon
16. eviCore
17. InterQual

**High Priority (Data/Analytics):**
18. Datavant
19. Clarify Health
20. Arcadia
21. Innovaccer
22. Health Catalyst

**High Priority (EHR):**
23. athenahealth
24. eClinicalWorks
25. Greenway Health
26. Veradigm
27. Epic (hard to get, but high volume)

**High Priority (Integration):**
28. Redox
29. Particle Health
30. Ribbon Health
31. b.well Connected Health
