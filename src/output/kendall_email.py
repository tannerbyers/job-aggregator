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
            subject = f"Kendall — {len(jobs)} healthcare roles today"

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
        sent_count = len(jobs)

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Georgia', serif; background: #f5f5f0; }}
    .container {{ max-width: 560px; margin: 0 auto; background: #ffffff; padding: 48px 40px; }}
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
    .job-company {{ font-size: 14px; color: #888880; margin-top: 4px; }}
    .job-salary {{ font-size: 15px; font-weight: 600; color: #2d5a4a; margin: 8px 0 4px; }}
    .job-salary-na {{ font-size: 13px; color: #aaa; margin: 8px 0 4px; font-style: italic; }}
    .job-why {{ font-size: 13px; color: #666660; line-height: 1.5; }}
    .job-meta {{ font-size: 12px; color: #aaa; margin-top: 10px; }}
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
            <div class="summary-number">{total_scanned}</div>
            <div class="summary-label">jobs scanned · {sent_count} matched your criteria</div>
        </div>

        <div class="jobs">
"""

        for job in jobs[:5]:
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

            why_fits = " · ".join(job.score_reasons[:2]) if job.score_reasons else "Strong match for your background"

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

            html += f"""
            <div class="job">
                <div class="job-header">
                    <div>
                        <div class="job-title">{job.title}</div>
                        <div class="job-company">{job.company}</div>
                    </div>
                </div>
                {salary_html}
                <div class="job-why">{why_fits}</div>
                {meta_html}
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
