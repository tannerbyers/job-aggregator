import os
from typing import Optional
from datetime import datetime, timedelta

import resend

from src.config import get_config


COMPANY_LOGO_URLS = {
    "Stripe": "https://logo.clearbit.com/stripe.com",
    "GitLab": "https://logo.clearbit.com/gitlab.com",
    "Smartsheet": "https://logo.clearbit.com/smartsheet.com",
    "Datadog": "https://logo.clearbit.com/datadog.com",
    "Cloudflare": "https://logo.clearbit.com/cloudflare.com",
    "Okta": "https://logo.clearbit.com/okta.com",
    "Twilio": "https://logo.clearbit.com/twilio.com",
    "MongoDB": "https://logo.clearbit.com/mongodb.com",
    "Elastic": "https://logo.clearbit.com/elastic.co",
    "Amplitude": "https://logo.clearbit.com/amplitude.com",
    "Wrike": "https://logo.clearbit.com/wrike.com",
    "LivePerson": "https://logo.clearbit.com/liveperson.com",
    "Intercom": "https://logo.clearbit.com/intercom.com",
    "Avum Inc.": None,
    "Worth AI": None,
    "Gritter Francona": None,
    "Upstream Rehabilitation": None,
}


def get_company_logo(company_name: str) -> Optional[str]:
    if company_name in COMPANY_LOGO_URLS:
        return COMPANY_LOGO_URLS[company_name]
    domain = company_name.lower().replace(" ", "").replace(".", "")
    return f"https://logo.clearbit.com/{domain}.com"


def get_days_ago(posted_at) -> Optional[int]:
    if not posted_at:
        return None
    try:
        return (datetime.utcnow() - posted_at.replace(tzinfo=None)).days
    except:
        return None


class EmailDigest:
    def __init__(self):
        self.config = get_config()
        if self.config.resend_api_key:
            resend.api_key = self.config.resend_api_key

    def send_digest(
        self,
        jobs: list,
        subject: Optional[str] = None,
        top_matches: Optional[list] = None,
        new_remote_us: Optional[list] = None,
        salary_visible: Optional[list] = None,
    ) -> dict:
        if not self.config.email_to:
            raise ValueError("EMAIL_TO not configured")

        if not jobs:
            print("No jobs to send, skipping email")
            return {"skipped": "no jobs"}

        html_content = self._build_html(jobs, top_matches, new_remote_us, salary_visible)

        if not subject:
            subject = f"Remote PM/PO Job Digest - {len(jobs)} matches"

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

    def _build_html(self, jobs: list, top_matches: Optional[list], new_remote_us: Optional[list], salary_visible: Optional[list]) -> str:
        html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 680px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
    .header h1 { margin: 0 0 10px; font-size: 24px; font-weight: 600; }
    .header p { margin: 0; opacity: 0.9; font-size: 14px; }
    .job-card { background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e8e8e8; }
    .job-header { display: flex; align-items: center; margin-bottom: 12px; }
    .job-logo { width: 40px; height: 40px; border-radius: 8px; margin-right: 12px; object-fit: contain; }
    .job-logo-placeholder { width: 40px; height: 40px; border-radius: 8px; margin-right: 12px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 600; color: #666; }
    .job-title { font-size: 16px; font-weight: 600; color: #1a1a1a; margin: 0; flex: 1; }
    .job-company { font-size: 14px; color: #666; margin: 4px 0 0 52px; }
    .job-badges { display: flex; gap: 8px; margin: 8px 0 12px 52px; flex-wrap: wrap; }
    .badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; }
    .badge-remote { background: #e8f5e9; color: #2e7d32; }
    .badge-new { background: #e3f2fd; color: #1565c0; }
    .badge-healthcare { background: #fce4ec; color: #c2185b; }
    .badge-salary { background: #fff3e0; color: #e65100; }
    .job-meta { display: flex; gap: 20px; font-size: 13px; color: #666; margin: 8px 0; }
    .job-meta span { display: flex; align-items: center; }
    .job-why { font-size: 12px; color: #888; margin: 10px 0; padding: 8px; background: #fafafa; border-radius: 6px; }
    .job-why strong { color: #555; }
    .apply-btn { display: inline-block; background: #667eea; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 14px; margin-top: 10px; }
    .apply-btn:hover { background: #5a6fd6; }
    .section-title { font-size: 14px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin: 25px 0 15px; }
    .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; margin-top: 30px; }
    .footer a { color: #667eea; text-decoration: none; }
    .score-badge { display: inline-block; background: #667eea; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; margin-left: 8px; }
</style>
</head>
<body>
    <div class="header">
        <h1>Remote PM/PO Job Digest</h1>
        <p>""" + datetime.now().strftime("%B %d, %Y") + """ | """ + str(len(jobs)) + """ matching jobs</p>
    </div>
"""

        for job in jobs[:25]:
            logo_url = get_company_logo(job.company)
            days_ago = get_days_ago(job.posted_at)

            html += '<div class="job-card">'
            html += '<div class="job-header">'
            if logo_url:
                html += f'<img src="{logo_url}" class="job-logo" alt="{job.company} logo" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'flex\'">'
                html += f'<div class="job-logo-placeholder" style="display:none">{job.company[0]}</div>'
            else:
                html += f'<div class="job-logo-placeholder">{job.company[0]}</div>'
            html += f'<h3 class="job-title">{job.title}<span class="score-badge">{job.score}</span></h3>'
            html += '</div>'
            html += f'<p class="job-company">{job.company}</p>'

            html += '<div class="job-badges">'
            if job.remote_type.value == "remote_us":
                html += '<span class="badge badge-remote">Remote US</span>'
            if days_ago is not None and days_ago <= 3:
                html += '<span class="badge badge-new">New!</span>'
            if any("healthcare" in r.lower() for r in job.score_reasons):
                html += '<span class="badge badge-healthcare">Healthcare</span>'
            if job.salary_min and job.salary_max:
                html += f'<span class="badge badge-salary">${job.salary_min // 1000}k-${job.salary_max // 1000}k</span>'
            html += '</div>'

            html += f'<div class="job-meta"><span>📍 {job.location}</span></div>'

            if job.score_reasons:
                html += f'<div class="job-why"><strong>Why:</strong> {" | ".join(job.score_reasons)}</div>'

            html += f'<a href="{job.apply_url}" class="apply-btn">Apply Now</a>'
            html += '</div>'

        html += """
    <div class="footer">
        <p>Sent by Job Aggregator | Matches updated Mon-Fri</p>
        <p><a href="#">Manage preferences</a> | <a href="#">Unsubscribe</a></p>
    </div>
</body>
</html>
"""
        return html
