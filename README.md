# No-Show Agents Dashboard

Interactive dashboard tracking no-show call outcomes per agent per country.

**Live site:** https://guillermohernandezauto1.github.io/NoShowAgents/

## What it shows

| Chart | Metric |
|---|---|
| KPI Row | Total submissions, reached, % reached, % at branch, % rescheduled |
| Customers Reached | Reached vs not reached by country / top agents |
| No-Show Reason Split | Breakdown of 14 recorded no-show reasons |
| % At Branch | Of customers reached, % who were physically at the branch |
| Problem at Branch | Rate and breakdown of 8 branch problem sub-types |
| Appointment Rescheduled % | Of customers reached, % who agreed to rebook |
| Trend Over Time | Any metric over months or weeks, by country or agent |
| Agent Performance Table | Full per-agent sortable breakdown |

## HQ + per-country builds

One generator, one template, many pages. A single run produces:

| Page | URL | Data |
|---|---|---|
| **HQ** (main) | `…/NoShowAgents/` | All countries |
| Per country | `…/NoShowAgents/de/`, `/es/`, `/fr/`, … | That country **only** |

Each country page contains *only* its own rows (real data isolation) and hides the
country selector. Because every page is generated from the **same template**, they
can never drift in format — the build even asserts the country pages are byte-for-byte
identical to HQ apart from the embedded data. To change anything, edit
`gen_dashboard.py` once and rerun; HQ and all country pages update together.

To restrict each country to its own page, put the per-country URLs behind an auth
layer (e.g. Cloudflare Access with Google Workspace) mapping each country group to
its path.

## Refreshing the data

See `CLAUDE.md` for the full automation prompt.

Quick version (builds HQ **and** every per-country page):
```bash
python3 gen_dashboard.py data/Monthly_Feed.csv data/Weekly_Feed.csv index.html
```

## Filters

- Year, Country (multi-select), Agent (searchable dropdown), Date range
- Monthly / Weekly tab toggle
- Per-chart view toggles: By Country · Top Agents · Table
