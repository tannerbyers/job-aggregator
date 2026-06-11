# Job Aggregator - Research Agent Brief

## Mission
Find additional job sources, refine filters, and improve job matching for a remote Product Owner/Product Manager candidate in healthcare.

---

## Current State

### Source Registry
**File:** `data/source_registry.json`

**Active Companies (18):**

| Company | Greenhouse Token | Industry | Priority |
|---------|------------------|---------|----------|
| Inovalon | inovalon | healthcare | 95 |
| Cohere Health | coherehealth | healthcare | 95 |
| Capital Rx | capitalrx | healthcare | 90 |
| Komodo Health | komodhealth | healthcare | 90 |
| MCG Health | mcghealth | healthcare | 85 |
| HealthVerity | healthverity | healthcare | 85 |
| QGenda | qgenda | healthcare | 85 |
| Tebra | tebra | healthcare | 85 |
| AdvancedMD | advancedmd | healthcare | 80 |
| Elation Health | elationhealth | healthcare | 80 |
| Luma Health | lumahealth | healthcare | 80 |
| 1upHealth | 1uphealth | healthcare | 80 |
| GitLab | gitlab | devops | 85 |
| Stripe | stripe | fintech | 85 |
| Smartsheet | smartsheet | saas | 80 |
| Datadog | datadog | devops | 80 |
| Wrike | wrike | saas | 75 |
| Intercom | intercom | communications | 75 |

---

## Candidate Profile

### Target Role
Remote Product Owner / Product Manager based in North Carolina

### Target Titles (22)
```
Product Owner
Product Manager
Technical Product Manager
Project Manager
Program Manager
Delivery Manager
Agile Project Manager
Agile Delivery Manager
Scrum Master
Product Operations Manager
Product Analyst
Business Analyst
Healthcare Product Manager
Claims Product Manager
Revenue Cycle Product Manager
Prior Authorization Product Manager
Interoperability Product Manager
FHIR Product Manager
EDI Product Manager
Payer Platform Product Manager
Provider Portal Product Manager
Healthcare Data Product Manager
```

### Include Keywords (21)
Used to match job titles that don't have exact title match:
```
product owner
product manager
technical product manager
project manager
program manager
delivery manager
agile project manager
agile delivery manager
scrum master
product operations
product analyst
business analyst
claims product
revenue cycle product
prior auth
interoperability
fhir product
edi product
payer platform
provider portal
healthcare data
```

### Exclude Keywords (21)
Jobs matching these in title are excluded:
```
intern
student
vp
vice president
director
senior director
principal
staff
engineering manager
sales
account executive
marketing manager
hardware
mechanical
warehouse
retail
nurse
physician
doctor
medical assistant
billing
coding
```

### Preferred Industries
```
Healthcare, Health Care, Medical, Hospital, Clinic, Insurance, SaaS, Fintech, B2B, Internal Tools, Cloud
```

### Remote Requirements
- Remote US only (no Canada, Europe, UK, etc.)
- Excludes hybrid and onsite
- Excludes "must be located in [state]" restrictions

---

## Scoring System

### Points Awarded
| Factor | Points |
|--------|--------|
| Remote US | +40 |
| Exact title match | +30 |
| Product-adjacent title | +20 |
| Salary visible | +15 |
| Recently posted (≤7 days) | +10 |
| Preferred industry | +10 |
| Healthcare company | +25 |
| Healthcare role | +15 |

### Minimum Score to Send
- 70 for daily digest

---

## Healthcare Companies to Research

### Full List (100 companies from healthcare-companies.txt)

**Best Fit - RCM/Claims/Payments:**
- Waystar
- Inovalon (ACTIVE)
- Zelis
- FinThrive
- Experian Health
- Edifecs
- Cognizant TriZetto
- HealthEdge
- Cotiviti
- MultiPlan
- R1 RCM
- Ensemble Health Partners

**Strong Fit - Value-Based Care/Payer Ops:**
- Optum Insight
- Change Healthcare / Optum
- Evolent Health
- Cohere Health (ACTIVE)
- Carelon
- eviCore healthcare
- MCG Health (ACTIVE)
- InterQual / Optum
- ZeOmega
- Medecision
- Softheon
- Lyric Health
- Vatica Health
- Reveleer
- Apixio

**Strong Fit - Healthcare Data/Analytics:**
- HealthVerity (ACTIVE)
- Datavant
- Komodo Health (ACTIVE)
- Clarify Health
- Arcadia
- Innovaccer
- Health Catalyst
- MedeAnalytics
- Milliman MedInsight
- Avaneer Health

**Best Fit - Provider Ops/Credentialing:**
- CAQH
- symplr
- Verisys
- Medallion
- Andros
- Modio Health

**Strong Fit - Provider Scheduling/Search:**
- QGenda (ACTIVE)
- Kyruus Health
- Phreesia

**Patient Billing/Payments:**
- Cedar
- Inbox Health
- PatientPay
- InstaMed / J.P. Morgan Healthcare Payments
- Flywire Healthcare
- Rectangle Health

**EHR/Practice Management:**
- athenahealth
- NextGen Healthcare
- eClinicalWorks
- Greenway Health
- Tebra (ACTIVE)
- AdvancedMD (ACTIVE)
- CareCloud
- ModMed
- Veradigm
- Epic
- Oracle Health
- MEDITECH
- Altera Digital Health
- Netsmart
- PointClickCare
- WellSky
- MatrixCare
- WebPT
- Therapy Brands
- RXNT
- Elation Health (ACTIVE)
- Canvas Medical
- Healthie
- DrChrono
- Kareo
- SimplePractice
- CentralReach

**Patient Access/Engagement:**
- Relatient
- Luma Health (ACTIVE)
- Artera
- Get Well
- NRC Health
- Press Ganey

**Pharmacy:**
- Surescripts
- DrFirst
- CoverMyMeds
- RxBenefits
- Capital Rx (ACTIVE)
- Navitus Health Solutions
- Omnicell

**Integration/FHIR:**
- Aidbox / Health Samurai
- Redox
- Zus Health
- Particle Health
- 1upHealth (ACTIVE)
- Ribbon Health
- b.well Connected Health

---

## ATS Types to Probe

For each company not in Greenhouse, check:

1. **Lever** - `https://api.lever.co/v0/postings/{slug}?mode=json`
2. **Ashby** - `https://api.ashbyhq.com/posting-api/job-board/{slug}`
3. **SmartRecruiters** - `https://api.smartrecruiters.com/public/v1/companies/{slug}/jobs`
4. **Workday** - often requires MyWorkday domain probing
5. **iCIMS** - often at jobs-{company}.icims.com
6. **Jobvite** - at {company}.jobvite.com

---

## Healthcare-Specific Title Keywords to Add

From healthcare-titles.txt:
```
Claims Product Manager
Revenue Cycle Product Manager
Prior Authorization Product Manager
Interoperability Product Manager
FHIR Product Manager
EDI Product Manager
Payer Platform Product Manager
Provider Portal Product Manager
Healthcare Data Product Manager
```

---

## Tasks for Research Agent

1. **Verify Greenhouse boards** - Test slugs for all 100 healthcare companies
2. **Probe Lever** - Check if any healthcare companies use Lever ATS
3. **Probe Ashby** - Check if any healthcare companies use Ashby ATS
4. **Find non-Greenhouse companies** - Document which ATS they use
5. **Suggest new titles** - Based on resume/role requirements
6. **Suggest new keywords** - Healthcare-specific terms that indicate good roles
7. **Identify missing companies** - Any big healthcare tech companies not on the list

---

## Output Format

For each company found:
```
Company Name | ATS Type | Slug/URL | PM Jobs Count | Remote PM Jobs | Notes
```

For each new source:
```
Source Type | URL Pattern | Companies Using | Job Count
```
