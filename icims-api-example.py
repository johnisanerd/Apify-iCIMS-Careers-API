"""
iCIMS API on Apify: pull live job postings from any iCIMS career site.

Actor:  https://apify.com/johnvc/icims-careers-api?fpr=9n7kx3
Token:  get a free Apify API key at https://apify.com?fpr=9n7kx3

Setup:
    uv sync
    cp .env.example .env      # then paste your token into .env
    uv run icims-api-example.py

Every run input below is deliberately small (one career site, a handful of
jobs, text-only descriptions) so your first run costs almost nothing. Raise
maxJobsPerSite / maxJobs once you have seen the output shape.
"""

import json
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR = "johnvc/icims-careers-api"

TOKEN = os.getenv("APIFY_TOKEN")
if not TOKEN:
    raise SystemExit(
        "Set APIFY_TOKEN in .env first. Free key: https://apify.com?fpr=9n7kx3"
    )

client = ApifyClient(TOKEN)


def run_actor(run_input: dict) -> list[dict]:
    """Start the Actor, wait for it to finish, return the dataset rows."""
    run = client.actor(ACTOR).call(run_input=run_input)
    dataset_id = run.default_dataset_id
    return list(client.dataset(dataset_id).iterate_items())


def show(rows: list[dict], limit: int = 3) -> None:
    """Print a short, readable summary of what came back."""
    jobs = [r for r in rows if r.get("result_type") == "job"]
    errors = [r for r in rows if r.get("result_type") == "error"]

    print(f"  {len(jobs)} jobs, {len(errors)} error rows")

    for job in jobs[:limit]:
        locations = ", ".join(job.get("locations_derived") or []) or "not stated"
        employment = ", ".join(job.get("employment_type") or []) or "not stated"
        print(f"  - {job.get('title')}")
        print(f"      req id:     {job.get('id')}")
        print(f"      employer:   {job.get('organization')}")
        print(f"      location:   {locations}  (remote: {job.get('remote_derived')})")
        print(f"      type:       {employment}")
        print(f"      posted:     {job.get('date_posted')}")
        print(f"      updated:    {job.get('date_updated')}")
        print(f"      category:   {job.get('category')}")
        print(f"      apply:      {job.get('apply_url')}")
        print(f"      url:        {job.get('url')}")

    for err in errors[:limit]:
        print(f"  ! {err.get('error_code')}: {err.get('error_message')}")


# ---------------------------------------------------------------------------
# Example 1: the wide tour. Most inputs at once, still cheap.
# ---------------------------------------------------------------------------
def run_full_example() -> list[dict]:
    """Show off most of the input schema against one career site."""
    run_input = {
        # Accepts a portal root, a sitemap URL, a search URL, a single job URL,
        # or a modern iCIMS career site on the employer's own domain.
        "startUrls": [{"url": "https://careers-rambus.icims.com"}],
        # Full job detail: description, salary, category, apply link.
        "includeDetails": True,
        # "both" also returns HTML; "text" alone keeps rows small and cheap.
        "descriptionFormat": "text",
        # Title filter, applied on the career site where the site supports it.
        "keywords": ["engineer"],
        # Small caps keep the first run inexpensive. 0 means no limit.
        "maxJobsPerSite": 5,
        "maxJobs": 5,
        "detailConcurrency": 5,
    }
    print("Example 1: full field tour, one iCIMS career site")
    rows = run_actor(run_input)
    show(rows)
    return rows


# ---------------------------------------------------------------------------
# Example 2: mirrors the "Track New iCIMS Job Postings Every Day" task.
# https://apify.com/johnvc/icims-careers-api/examples/track-new-icims-job-postings?fpr=9n7kx3
# ---------------------------------------------------------------------------
def run_track_new_postings() -> list[dict]:
    """Change detection: only jobs that moved inside the last 7 days.

    newerThan accepts an ISO date ("2026-08-01"), a full timestamp, or a
    relative window like "24h", "7d", "2w". On the classic portal surface the
    window is applied to the sitemap before any job page is fetched, so
    unchanged jobs cost nothing at all. Pair it with includeDetails=False for
    the cheapest possible daily poll.
    """
    run_input = {
        "startUrls": [{"url": "https://careers-rambus.icims.com"}],
        "newerThan": "7d",
        # "updated" catches edits as well as new reqs; "posted" is new-only.
        "cutoffField": "updated",
        # List-only mode: url, id, title, dates. No detail pages fetched.
        "includeDetails": False,
        "maxJobsPerSite": 10,
    }
    print("\nExample 2: only jobs changed in the last 7 days (list-only)")
    rows = run_actor(run_input)
    show(rows)
    return rows


# ---------------------------------------------------------------------------
# Example 3: mirrors "Find Companies Using iCIMS and Pull Their Jobs".
# https://apify.com/johnvc/icims-careers-api/examples/companies-that-use-icims?fpr=9n7kx3
# ---------------------------------------------------------------------------
def run_companies_by_name() -> list[dict]:
    """Skip the URLs: pass company names and let the Actor resolve them.

    Each name is resolved to its iCIMS tenant, so you can build a watchlist of
    employers without looking up a single career-site URL.
    """
    run_input = {
        "companies": ["rambus"],
        "includeDetails": True,
        "descriptionFormat": "text",
        "maxJobsPerSite": 3,
    }
    print("\nExample 3: company names instead of URLs")
    rows = run_actor(run_input)
    show(rows)
    return rows


# ---------------------------------------------------------------------------
# Example 4: mirrors "Scrape Job Postings From a Career Site".
# https://apify.com/johnvc/icims-careers-api/examples/scrape-job-postings-career-site?fpr=9n7kx3
# ---------------------------------------------------------------------------
def run_single_career_site() -> list[dict]:
    """The plainest call there is: one career site in, structured jobs out."""
    run_input = {
        "startUrls": [{"url": "https://careers-rambus.icims.com"}],
        "descriptionFormat": "markdown",
        "maxJobsPerSite": 3,
    }
    print("\nExample 4: one career site, markdown descriptions")
    rows = run_actor(run_input)
    show(rows)
    return rows


if __name__ == "__main__":
    rows = run_full_example()

    # Uncomment any of these to try the other recipes. Each one is a separate
    # Actor run, so each one bills separately.
    # run_track_new_postings()
    # run_companies_by_name()
    # run_single_career_site()

    # Full shape of the first row, so you can see every field available.
    if rows:
        print("\nFirst row, complete:")
        print(json.dumps(rows[0], indent=2, default=str)[:2000])
