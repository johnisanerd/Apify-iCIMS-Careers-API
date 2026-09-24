# iCIMS API: Pull Live Job Postings From Any iCIMS Career Site

iCIMS does not hand out a public read API for job postings, so most teams end up writing a one-off parser per employer. This repo shows you the shortcut: a working Python example plus MCP install steps for the [iCIMS Careers API](https://apify.com/johnvc/icims-careers-api?fpr=9n7kx3) on Apify.

Point it at a career site, get back structured jobs: title, requisition ID, employer, locations, employment type, posted and updated dates, salary when the employer publishes it, and the apply link. It reads both public iCIMS surfaces, the classic `careers-{tenant}.icims.com` portals and the modern iCIMS career sites that live on the employer's own domain, so you do not have to know which one an employer runs.

Get a free Apify API key here: https://apify.com?fpr=9n7kx3

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/hqdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

## Text walkthrough

The **icims api** you are looking for is this Actor. You give it one thing, a career site, either as a URL in `startUrls` or as a plain company name in `companies`, and it works out which iCIMS surface that employer is on before it fetches anything. Every live requisition comes back as one row: `title`, `id` (the employer's own req number), `organization`, `locations_derived`, `employment_type`, `date_posted`, `date_updated`, `description_text`, `salary_raw`, and `apply_url`. The field names deliberately match the common job-feed conventions, so rows drop into an existing pipeline without a mapping layer.

The part that saves real money is `newerThan`. Set it to `7d` and the Actor filters on the site's own last-modified data **before** it opens any job page, so a daily poll of an employer with 400 open reqs costs you the handful that actually moved. Add `includeDetails: false` and you get a pure change feed: url, id, title, dates. That is exactly the shape behind the [Track New iCIMS Job Postings Every Day](https://apify.com/johnvc/icims-careers-api/examples/track-new-icims-job-postings?fpr=9n7kx3) recipe, which a recruiting team can run on a schedule and pipe into Slack.

Sites that fail are not silent. A dead tenant, an IP-restricted portal, or a domain that turns out not to be iCIMS at all comes back as a labelled error row with an `error_code`, so an automated job can tell "no new jobs" apart from "this employer moved off iCIMS".

## Quick start

```bash
git clone https://github.com/johnisanerd/Apify-iCIMS-Careers-API.git
cd Apify-iCIMS-Careers-API
uv sync
cp .env.example .env
```

Paste your Apify token into `.env`, then:

```bash
uv run icims-api-example.py
```

That first run pulls five jobs from one career site with text descriptions, which keeps it close to free. Every input in `icims-api-example.py` is annotated so you can widen it deliberately.

## Recipes

Ready-made input sets, each one a live page on the Apify Store you can run without writing any code:

| Recipe | What it does |
|---|---|
| [Get iCIMS Job Data Without the Official API](https://apify.com/johnvc/icims-careers-api/examples/icims-jobs-without-official-api?fpr=9n7kx3) | The starting point when you searched for iCIMS API documentation and found nothing public. |
| [Track New iCIMS Job Postings Every Day](https://apify.com/johnvc/icims-careers-api/examples/track-new-icims-job-postings?fpr=9n7kx3) | Change detection only. Cheap enough to run daily on a big employer. |
| [Find Companies Using iCIMS and Pull Their Jobs](https://apify.com/johnvc/icims-careers-api/examples/companies-that-use-icims?fpr=9n7kx3) | Pass a watchlist of company names, skip the URL hunting. |
| [Scrape Job Postings From a Career Site](https://apify.com/johnvc/icims-careers-api/examples/scrape-job-postings-career-site?fpr=9n7kx3) | One employer, full job detail, the plainest possible call. |
| [iCIMS as an ATS API for Your Own Tools](https://apify.com/johnvc/icims-careers-api/examples/icims-ats-api-integration?fpr=9n7kx3) | Treat iCIMS like the read API it does not ship, from your own backend. |

**Schedule tip:** any of these can run on a timer. In the Apify Console open the Actor, click **Schedules**, and add a daily or weekly cron. Combine a schedule with `newerThan: "24h"` and `includeDetails: false` and you have a job-change feed that costs a fraction of a full crawl.

## Input parameters

| Parameter | Type | Default | What it does |
|---|---|---|---|
| `startUrls` | array of `{url}` | Rambus career site | Portal root, sitemap URL, search URL, single job URL, or a modern career site on the employer's domain. |
| `companies` | array of strings | empty | Company names. Resolved to iCIMS tenants for you. |
| `newerThan` | string | not set | ISO date, full timestamp, or a window like `24h`, `7d`, `2w`. Filters before fetching job pages. |
| `cutoffField` | string | `updated` | `updated` catches edits too; `posted` returns new requisitions only. |
| `includeDetails` | boolean | `true` | `false` gives list-only rows: url, id, title, dates. The cheap monitoring mode. |
| `descriptionFormat` | string | `both` | `both`, `text`, `html`, or `markdown`. |
| `keywords` | array of strings | empty | Title filter. Applied server side where the career site supports it. |
| `maxJobsPerSite` | integer | `0` | Cap per career site. `0` means every job. |
| `maxJobs` | integer | `0` | Global cap across all sites. |
| `detailConcurrency` | integer | `5` | Parallel detail requests, maximum 10. |
| `proxyConfiguration` | object | off | Optional. Only needed for the small number of tenants that restrict traffic by network. |

## Output fields

Each row carries `result_type`, either `job` or `error`.

`url`, `id`, `title`, `organization`, `organization_url`, `description_text`, `description_html`, `description_markdown`, `employment_type`, `locations_derived`, `remote_derived`, `date_posted`, `date_updated`, `date_validthrough`, `salary_raw`, `category`, `additional_fields`, `apply_url`, `latitude`, `longitude`, `tenant`, `source`, `source_type`, `source_surface`, `source_domain`, `source_url`, `scraped_at`, and on error rows `error_code` and `error_message`.

The dataset ships two views. **Overview** is the full table. **Changes** is the monitoring view: url, date_updated, date_posted, title, which is the only shape you need when you are diffing runs.

---

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the iCIMS API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings > Connectors** (or **Settings > Developer > Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/icims-careers-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the iCIMS API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/icims-careers-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/icims-careers-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the iCIMS API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings > Connectors > Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/icims-careers-api`.
3. In any chat, open **+ > Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/icims-careers-api`, using OAuth when prompted.
5. Ask Claude to run the iCIMS API.

Open Claude on the web: https://claude.ai

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/icims-careers-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/icims-careers-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor > Settings > MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the iCIMS API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/icims-careers-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

<!-- ask-ai:start -->
## 🤖 Ask an AI assistant about this Actor

Open a ready-to-send prompt about the iCIMS Careers API in the AI of your choice:

- 💬 [ChatGPT](https://chatgpt.com/?q=Using%20the%20iCIMS%20Careers%20API%20on%20Apify%20%28https://apify.com/johnvc/icims-careers-api?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Find%20Companies%20Using%20iCIMS%20and%20Pull%20Their%20Jobs%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
- 🧠 [Claude](https://claude.ai/new?q=Using%20the%20iCIMS%20Careers%20API%20on%20Apify%20%28https://apify.com/johnvc/icims-careers-api?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Find%20Companies%20Using%20iCIMS%20and%20Pull%20Their%20Jobs%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
- 🔍 [Perplexity](https://www.perplexity.ai/search?q=Using%20the%20iCIMS%20Careers%20API%20on%20Apify%20%28https://apify.com/johnvc/icims-careers-api?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Find%20Companies%20Using%20iCIMS%20and%20Pull%20Their%20Jobs%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
- 🅒 [Copilot](https://copilot.microsoft.com/?q=Using%20the%20iCIMS%20Careers%20API%20on%20Apify%20%28https://apify.com/johnvc/icims-careers-api?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Find%20Companies%20Using%20iCIMS%20and%20Pull%20Their%20Jobs%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
<!-- ask-ai:end -->

## FAQ

**Is there an official iCIMS API for job postings?**
Not a public one you can sign up for. iCIMS sells integration access to its own customers, so if you want postings from an employer you do not work for, the public career site is the surface you have. This Actor reads that surface and hands you the same structured fields an API would.

**Does it work on both kinds of iCIMS site?**
Yes. Classic portals on `icims.com` and modern iCIMS career sites hosted on the employer's own domain are both supported. The Actor probes the domain and picks the right path, so you can pass either and not think about it.

**How do I scrape job postings without hammering the site?**
Use `newerThan`. On the classic portal surface the filter is applied to the site's own change data before any job page is opened, so an unchanged requisition is never fetched. Add `includeDetails: false` and a run touches one page per site.

**Can I use this as an ATS API inside my own product?**
That is what most people do with it. Call it from your backend with the Apify client, or from n8n, or over MCP from an agent. The output field names follow common job-feed conventions, so a normalizer you already have will usually ingest it unchanged.

**What happens when a career site is dead or restricted?**
You get a row with `result_type: "error"` and an `error_code` such as `tenant_not_found`, `ip_gated`, or `not_icims`, rather than a crashed run. A watchlist job can act on that: the employer moved off iCIMS, or the tenant retired.

**How much does a run cost?**
Pricing is on the [Actor page](https://apify.com/johnvc/icims-careers-api?fpr=9n7kx3) and bills per delivered job row, so a monitoring run that finds two changed jobs costs two rows, not a full crawl. Check the live pricing there rather than trusting a number copied into a README.

**Which fields can I count on?**
`url`, `id`, `title`, `organization`, and `date_updated` are present on every job row. Salary, category, and coordinates depend on what the employer publishes, so they can be null.

## People also search for

icims api, icims ats, icims jobs, ats api, job data api, scrape job postings, applicant tracking system api, job posting api, companies that use icims, icims api documentation, icims mcp server, track new icims job postings, career site job data, job listings api

## n8n integration

Available as an n8n community node, **[n8n-nodes-icims-careers-api](https://www.npmjs.com/package/n8n-nodes-icims-careers-api)**. In n8n: Settings, Community Nodes, install `n8n-nodes-icims-careers-api`, then use it in any workflow (it also works as an AI Agent tool).

## More

- Actor on the Apify Store: https://apify.com/johnvc/icims-careers-api?fpr=9n7kx3
- Free Apify account: https://apify.com?fpr=9n7kx3
- Apify Python client docs: https://docs.apify.com/api/client/python/
- Apify MCP docs: https://docs.apify.com/platform/integrations/mcp
- uv: https://docs.astral.sh/uv/

Last Updated: 2026.09.22
