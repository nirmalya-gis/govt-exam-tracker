# Government exam tracker (West Bengal, Geography / RS-GIS postgraduate)

- `index.html` renders the guide. `data.json` holds the curated exam details. `notices.json` is written by the bot.
- `.github/workflows/update.yml` runs daily, detects new matching notices on ssc.gov.in, psc.wb.gov.in and prb.wb.gov.in, commits them to `notices.json`, and opens a GitHub issue.
- When an issue appears, open the notice, then edit `data.json` (dates, fee, syllabus) and set `last_reviewed`.

## Setup
1. Create a repo and push these files to `main`.
2. Settings > Pages > Deploy from branch > `main` / root.
3. Settings > Actions > General > Workflow permissions: Read and write.
4. Run the workflow once from the Actions tab (workflow_dispatch) and read the log.

## Limits
Detection matches keywords in link text on each site's home page. If a site changes layout, blocks GitHub's servers, or posts notices only inside PDFs, the bot will miss them. Treat it as an alert, not a source of truth.
