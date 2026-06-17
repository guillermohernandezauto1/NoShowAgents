# No-Show Agents Dashboard — Automation Instructions

## Live Dashboard
https://guillermohernandezauto1.github.io/NoShowAgents/

## Refresh Workflow

Run this prompt to pull the latest data from Google Drive and push an updated dashboard:

---

Check the Google Drive folder https://drive.google.com/drive/folders/1-iI6s5D87r_G0Q7ZsbsoZRCHOxES7nCP

1. Download the two latest CSV files to `downloads/feeds_new/`:
   - `Monthly_Feed.csv` (file ID: 1HxTLziAAkI_JddQjS6JehVbmSXB4aRuP)
   - `Weekly_Feed.csv`  (file ID: 1iYZAK-hdzGuN2XAteJm7bzb2JxdolG81)

2. Run the generator:
   ```
   python3 repo_noshowagents/gen_dashboard.py \
     downloads/feeds_new/Monthly_Feed.csv \
     downloads/feeds_new/Weekly_Feed.csv \
     repo_noshowagents/index.html
   ```

3. Copy updated CSVs into the repo data directory:
   ```
   cp downloads/feeds_new/Monthly_Feed.csv repo_noshowagents/data/
   cp downloads/feeds_new/Weekly_Feed.csv  repo_noshowagents/data/
   ```

4. Push everything to GitHub:
   ```
   cd repo_noshowagents
   git add index.html data/Monthly_Feed.csv data/Weekly_Feed.csv
   git commit -m "Dashboard refresh [today's date]"
   git push origin main
   ```

5. Report: rows in each CSV, file size of index.html, git push SHA.

---

## File Structure

```
NoShowAgents/
├── index.html          ← The live dashboard (auto-generated, do not edit manually)
├── gen_dashboard.py    ← Generator script — edit this to change charts or formulas
├── data/
│   ├── Monthly_Feed.csv   ← Latest monthly data (agent × country × month)
│   └── Weekly_Feed.csv    ← Latest weekly data  (agent × country × week)
└── README.md
```

## Formulas Reference

| Metric | Formula |
|---|---|
| % Reached | `reached_yes / total_submissions` |
| % At Branch | `at_branch_yes / reached_yes` |
| % Rescheduled | `result_new_appt / reached_yes` |
| Problem Rate | `rows with any pb_* > 0 summed by reached_yes / total reached_yes` |
| Reason split % | each reason / SUM(all reasons) |
| PB sub-reason % | each pb_* / SUM(all pb_*) |
