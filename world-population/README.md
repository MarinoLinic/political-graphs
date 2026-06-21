# UN WPP2024 Population Pipeline

## Setup (one-time)
1. Put the source file here, with this exact name:
   ```
   data/WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx
   ```
   Download it from:
   https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/EXCEL_FILES/2_Population/WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx

2. Install the one dependency:
   ```
   pip install openpyxl
   ```

(`data/country_region_mapping.csv` is already included — it maps all 237
countries/areas in the file to the 10 regions used throughout this project.)

## Run
```
python3 run_all.py
```
Optionally pass a year (defaults to 2025):
```
python3 run_all.py 2030
```

## Output
```
output/csv/country_data_2025.csv   — per-country raw + derived figures
output/csv/region_summary.csv      — rolled up into the 10 regions
output/txt/population_summary.md   — formatted bar-chart text blocks
```

That's it — one command, no other input needed.

## Project layout
```
data/
  WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx  (you add this)
  country_region_mapping.csv   (included)
scripts/
  extract_country_data.py      (script 1/3 — unchanged from original)
  aggregate_by_region.py       (script 2/3 — unchanged from original)
  generate_summary_text.py     (script 3/3 — unchanged from original)
run_all.py                     (the only script you actually run)
```

## Notes
- The three pipeline scripts themselves were not modified — `run_all.py`
  just calls them in order with the right paths and working directories.
- If `country_region_mapping.csv` is ever missing a country (e.g. the UN
  adds a new entry in a future WPP release), `aggregate_by_region.py`
  will print an "UNMATCHED" warning to the console rather than silently
  dropping it — check that output if numbers look off after a refresh.
