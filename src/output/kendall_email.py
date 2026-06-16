from typing import Optional
from datetime import datetime

import resend

from src.config import get_config


class EmailDigest:
    def __init__(self):
        self.config = get_config()
        if self.config.resend_api_key:
            resend.api_key = self.config.resend_api_key

    def send_digest(
        self,
        jobs: list,
        total_scanned: int = 0,
        subject: Optional[str] = None,
    ) -> dict:
        if not self.config.email_to:
            raise ValueError("EMAIL_TO not configured")

        if not jobs:
            print("No jobs to send, skipping email")
            return {"skipped": "no jobs"}

        html_content = self._build_html(jobs, total_scanned)

        if not subject:
            subject = f"Kendall - {len(jobs)} PM/PO role matches today"

        params = {
            "from": self.config.email_from,
            "to": self.config.email_to,
            "subject": subject,
            "html": html_content,
        }

        if self.config.resend_api_key and self.config.resend_api_key != "placeholder_update_me":
            result = resend.Emails.send(params=params)
            print(f"Email sent: {result}")
            return result
        else:
            print(f"[DRY RUN] Would send email: {params}")
            return {"dry_run": True}

    def _build_html(self, jobs: list, total_scanned: int = 0) -> str:
        today = datetime.now().strftime("%B %d, %Y")
        
        # Group by company and keep the best scoring job per company
        company_jobs = {}
        for job in jobs:
            company_lower = job.company.lower()
            if company_lower not in company_jobs or job.score > company_jobs[company_lower].score:
                company_jobs[company_lower] = job
        
        # Sort: jobs with salary first, then by score
        grouped_jobs = list(company_jobs.values())
        grouped_jobs.sort(key=lambda j: (
            -bool(j.salary_min and j.salary_max),  # Salary visible comes first
            -j.score  # Then by score (descending)
        ))
        
        sent_count = len(grouped_jobs)

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Georgia', serif; background: #f5f5f0; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 48px 40px; }}
    .header {{ text-align: center; margin-bottom: 40px; border-bottom: 1px solid #e8e8e4; padding-bottom: 32px; }}
    .header h1 {{ font-size: 22px; font-weight: normal; color: #1a1a1a; letter-spacing: -0.3px; }}
    .header p {{ font-size: 13px; color: #888880; margin-top: 8px; }}
    .summary {{ text-align: center; padding: 32px 0; }}
    .summary-number {{ font-size: 56px; font-weight: 300; color: #2d5a4a; letter-spacing: -2px; line-height: 1; }}
    .summary-label {{ font-size: 14px; color: #666660; margin-top: 8px; }}
    .job {{ padding: 24px 0; border-bottom: 1px solid #f0f0ec; }}
    .job:last-child {{ border-bottom: none; }}
    .job-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }}
    .job-title {{ font-size: 16px; color: #1a1a1a; font-weight: 600; line-height: 1.3; }}
    .job-score {{ font-size: 14px; font-weight: 600; color: #2d5a4a; background: #f0f5f3; padding: 3px 8px; border-radius: 3px; white-space: nowrap; }}
    .job-company {{ font-size: 14px; color: #888880; margin-top: 4px; }}
    .job-location {{ font-size: 13px; color: #999; margin-top: 2px; }}
    .job-salary {{ font-size: 15px; font-weight: 600; color: #2d5a4a; margin: 12px 0 4px; background: #f0f5f3; padding: 8px 12px; border-radius: 4px; }}
    .job-salary-na {{ font-size: 13px; color: #aaa; margin: 12px 0 4px; font-style: italic; }}
    .job-why {{ font-size: 13px; color: #666660; line-height: 1.5; margin: 8px 0; }}
    .job-description {{ font-size: 12px; color: #888880; line-height: 1.6; margin: 10px 0; padding: 10px 12px; background: #fafaf8; border-left: 3px solid #e8e8e4; }}
    .job-meta {{ font-size: 12px; color: #aaa; margin-top: 10px; }}
    .apply-btn {{ display: inline-block; background: #3b6b4a; color: #ffffff; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600; margin-top: 16px; }}
    .apply-btn:hover {{ background: #2f5a3f; }}
    .footer {{ text-align: center; padding-top: 32px; margin-top: 32px; border-top: 1px solid #e8e8e4; }}
    .footer p {{ font-size: 12px; color: #aaa; line-height: 1.8; }}
    .footer a {{ color: #888880; text-decoration: underline; }}
    .preferences-link {{ color: #888880; text-decoration: underline; }}
</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Kendall Job Matches</h1>
            <p>{today}</p>
        </div>

        <div class="summary">
            <div class="summary-number">{sent_count}</div>
            <div class="summary-label">companies with PM/PO roles · {total_scanned} jobs scanned</div>
        </div>

        <div class="jobs">
"""

        for job in grouped_jobs:
            posted_str = ""
            if job.posted_at:
                try:
                    days = (datetime.utcnow() - job.posted_at.replace(tzinfo=None)).days
                    if days == 0:
                        posted_str = "Posted today"
                    elif days == 1:
                        posted_str = "Posted yesterday"
                    elif days <= 7:
                        posted_str = f"Posted {days} days ago"
                except:
                    posted_str = ""

            why_fits = " · ".join(job.score_reasons[:3]) if job.score_reasons else "Strong match"

            salary_html = ""
            if job.salary_min and job.salary_max:
                salary_html = f'<div class="job-salary">${job.salary_min:,}–${job.salary_max:,}</div>'
            elif job.salary_min:
                salary_html = f'<div class="job-salary">${job.salary_min:,}+</div>'
            else:
                salary_html = '<div class="job-salary-na">Salary not listed</div>'

            meta_html = ""
            if posted_str:
                meta_html = f'<div class="job-meta">{posted_str}</div>'
            
            # Extract description snippet (first 150 chars, clean)
            description_html = ""
            if job.description:
                desc_snippet = job.description.strip()[:150]
                # Remove excessive whitespace/newlines
                desc_snippet = " ".join(desc_snippet.split())
                if len(job.description) > 150:
                    desc_snippet += "..."
                if desc_snippet:
                    description_html = f'<div class="job-description">{desc_snippet}</div>'

            html += f"""
            <div class="job">
                <div class="job-header">
                    <div style="flex: 1;">
                        <div class="job-title">{job.title}</div>
                        <div class="job-company">{job.company}</div>
                        <div class="job-location">{job.location}</div>
                    </div>
                    <div class="job-score">Score: {job.score}</div>
                </div>
                {salary_html}
                <div class="job-why">{why_fits}</div>
            {description_html}
            {meta_html}
            <a href="{job.apply_url}" class="apply-btn">Apply</a>
            </div>
"""

        html += """
        </div>

        <div class="footer">
            <p>
                <a href="mailto:pause+kendall@decoupledev.com?subject=Pause%20emails">Pause emails</a>
                · <a href="mailto:prefs+kendall@decoupledev.com?subject=Frequency%20change">Change frequency</a>
                · <a href="mailto:unsubscribe+kendall@decoupledev.com?subject=Unsubscribe">Unsubscribe</a>
            </p>
            <p style="margin-top: 16px; font-size: 11px;">
                Jobs at decoupledev.com
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html
