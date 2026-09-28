MANUAL DOWNLOAD INSTRUCTION
=============================
Because Dataful requires interactive sign-in (no direct CSV URL exposed via public endpoint),
download the three datasets manually via browser:

1. https://dataful.in/datasets/22567/ -> Download CSV -> rename: mplads_18th_recommended_works.csv
2. https://dataful.in/datasets/22566/ -> Download CSV -> rename: mplads_18th_completed_works.csv
3. https://dataful.in/datasets/22565/ -> Download CSV -> rename: mplads_18th_vendor_expenditure.csv

Then place all three in this folder (data/input/).

After placement, run:
  cd backend && python ingest.py data/input/mplads_18th_recommended_works.csv
  cd backend && python ingest.py data/input/mplads_18th_completed_works.csv

Vendor data: do NOT force-join to work-level records via MP/constituency/agency alone.
Only link via exact unique_work_number when present, else keep separate.

Source provenance for all three: PUBLIC_OTHER_GOV_SOURCE / DATAFUL / upstream MOSPI/eSAKSHI.
