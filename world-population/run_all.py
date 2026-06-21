#!/usr/bin/env python3
"""
run_all.py — runs the full WPP2024 population pipeline end to end.

USAGE (zero thinking required):
    1. Put the UN source file here:
         data/WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx
    2. python3 run_all.py
       (optionally: python3 run_all.py 2030   to run for a different year)

WHAT IT DOES (in order):
    scripts/extract_country_data.py   data/<xlsx>           -> output/csv/country_data_<year>.csv
    scripts/aggregate_by_region.py    + data/country_region_mapping.csv -> output/csv/region_summary.csv
    scripts/generate_summary_text.py                         -> output/txt/population_summary.md

Nothing else to configure. If the xlsx isn't where it's expected, this
script tells you the exact UN download URL and stops (it does not
silently try to download a 60MB file for you).
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUT_DIR = BASE_DIR / "output"
CSV_DIR = OUTPUT_DIR / "csv"
TXT_DIR = OUTPUT_DIR / "txt"

XLSX_NAME = "WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx"
XLSX_PATH = DATA_DIR / XLSX_NAME
MAPPING_PATH = DATA_DIR / "country_region_mapping.csv"

SOURCE_URL = (
    "https://population.un.org/wpp/assets/Excel%20Files/"
    "1_Indicator%20(Standard)/EXCEL_FILES/2_Population/"
    "WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx"
)


def run(cmd, cwd):
    print(f"\n$ {' '.join(str(c) for c in cmd)}   (cwd={cwd})")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"\n*** Step failed (exit code {result.returncode}): "
              f"{' '.join(str(c) for c in cmd)}", file=sys.stderr)
        sys.exit(result.returncode)


def main():
    year = sys.argv[1] if len(sys.argv) > 1 else "2025"

    if not XLSX_PATH.exists():
        print(f"*** Missing source file:\n    {XLSX_PATH}\n\n"
              f"Download it from:\n    {SOURCE_URL}\n\n"
              f"and save it into the data/ folder with that exact filename, "
              f"then re-run this script.", file=sys.stderr)
        sys.exit(1)

    if not MAPPING_PATH.exists():
        print(f"*** Missing region mapping file:\n    {MAPPING_PATH}",
              file=sys.stderr)
        sys.exit(1)

    CSV_DIR.mkdir(parents=True, exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: per-country extraction -> output/csv/country_data_<year>.csv
    run(
        ["python3", str(SCRIPTS_DIR / "extract_country_data.py"),
         str(XLSX_PATH), year],
        cwd=CSV_DIR,
    )
    country_csv = CSV_DIR / f"country_data_{year}.csv"

    # Step 2: roll up into regions -> output/csv/region_summary.csv
    run(
        ["python3", str(SCRIPTS_DIR / "aggregate_by_region.py"),
         str(country_csv), str(MAPPING_PATH)],
        cwd=CSV_DIR,
    )
    region_csv = CSV_DIR / "region_summary.csv"

    # Step 3: render summary text -> output/txt/population_summary.md
    run(
        ["python3", str(SCRIPTS_DIR / "generate_summary_text.py"),
         str(region_csv)],
        cwd=TXT_DIR,
    )

    print("\n" + "=" * 60)
    print("Done. Outputs:")
    print(f"  {country_csv}")
    print(f"  {region_csv}")
    print(f"  {TXT_DIR / 'population_summary.md'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
