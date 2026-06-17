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

## Refreshing the data

See `CLAUDE.md` for the full automation prompt.

Quick version:
```bash
python3 gen_dashboard.py data/Monthly_Feed.csv data/Weekly_Feed.csv index.html
```

## Filters

- Year, Country (multi-select), Agent (searchable dropdown), Date range
- Monthly / Weekly tab toggle
- Per-chart view toggles: By Country · Top Agents · Table
