#!/usr/bin/env python3
"""Resubmit sitemap.xml to Google Search Console (sc-domain:db9v12.co.uk).

Runs in the IndexNow workflow after each Pages build. Authenticates as the service account
sitemap-updater@zoob-sites-search.iam.gserviceaccount.com, whose JSON key comes from env
GSC_SA_KEY (GitHub secret) or the file named in GSC_SA_FILE; needs google-auth + requests.
Never fails the job: problems are printed as warnings. Google answers HTTP 204 on success.
"""
import json
import os
import urllib.parse

HOST = "db9v12.co.uk"


def main() -> None:
    raw = os.environ.get("GSC_SA_KEY") or (open(os.environ["GSC_SA_FILE"]).read() if os.environ.get("GSC_SA_FILE") else "")
    if not raw:
        print("Google: no GSC_SA_KEY, skipped.")
        return
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
        creds = service_account.Credentials.from_service_account_info(
            json.loads(raw), scopes=["https://www.googleapis.com/auth/webmasters"])
        site = urllib.parse.quote(f"sc-domain:{HOST}", safe="")
        feed = urllib.parse.quote(f"https://{HOST}/sitemap.xml", safe="")
        r = AuthorizedSession(creds).put(f"https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}", timeout=30)
        print(f"Google: sitemap resubmitted, HTTP {r.status_code}" if r.ok
              else f"::warning::Google sitemap resubmit refused: HTTP {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"::warning::Google sitemap resubmit failed: {type(e).__name__}")


if __name__ == "__main__":
    main()
