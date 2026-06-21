"""
SCRIPT 2 of 3 — aggregate_by_region.py

Takes the per-country CSV produced by extract_country_data.py and rolls it
up into the custom regions defined in country_region_mapping.csv (the
same 10 regions used throughout this project). No UN data is touched
here — this is pure aggregation of script 1's output.

Usage:
    python3 aggregate_by_region.py [country_csv] [mapping_csv]

Output:
    region_summary.csv — one row per region with, for each of the five
    metrics (TotalPop, Under40, Under18, Age0to4, Over65):
      {Metric}_M       — regional total, in millions
      {Metric}_pct      — that metric as a % of the REGION's own total
                          population (e.g. Under40_pct = 68.3 means 68.3%
                          of South Asia's population is under 40)
    plus CountryCount, sorted by TotalPop_M descending.

    Note: {Metric}_pct here is a share of the region's own population,
    not a share of the world total for that metric. The latter (used for
    the "South Asia: 27% of the world's under-40s" style figures) is
    computed separately in script 3, generate_summary_text.py, since it
    needs the world totals across all regions.

Any country present in country_csv but missing from mapping_csv is
reported and excluded from the totals, rather than silently dropped —
check the console output for an "UNMATCHED" section before trusting the
regional numbers.
"""

import csv
import sys
from collections import defaultdict

DEFAULT_COUNTRY_CSV = "country_data_2025.csv"
DEFAULT_MAPPING_CSV = "country_region_mapping.csv"

METRICS = ["TotalPop", "Under40", "Under20", "Age0to4", "Over65"]


def main():
    country_csv = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_COUNTRY_CSV
    mapping_csv = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MAPPING_CSV

    # Load mapping: ISO3 -> region
    region_by_iso3 = {}
    with open(mapping_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            region_by_iso3[row["ISO3"]] = row["Region"]

    # Load country data and aggregate
    totals = {m: defaultdict(float) for m in METRICS}
    counts = defaultdict(int)
    unmatched = []

    with open(country_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            iso3 = row["ISO3"]
            region = region_by_iso3.get(iso3)

            if region is None:
                unmatched.append((row["Country"], iso3))
                continue

            for m in METRICS:
                totals[m][region] += float(row[f"{m}_thousands"])
            counts[region] += 1

    if unmatched:
        print(f"\n*** {len(unmatched)} countries from {country_csv} have "
              f"no entry in {mapping_csv} and were EXCLUDED: ***",
              file=sys.stderr)
        for name, iso3 in unmatched:
            print(f"  {name} ({iso3})", file=sys.stderr)
        print("Add them to the mapping file and re-run if this matters.\n",
              file=sys.stderr)

    regions = sorted(totals["TotalPop"], key=lambda r: totals["TotalPop"][r],
                      reverse=True)

    out_path = "region_summary.csv"
    fieldnames = ["Region", "CountryCount"]
    for m in METRICS:
        fieldnames += [f"{m}_M", f"{m}_pct"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in regions:
            pop_m = totals["TotalPop"][r] / 1000
            row = {"Region": r, "CountryCount": counts[r]}
            for m in METRICS:
                m_m = totals[m][r] / 1000
                row[f"{m}_M"] = round(m_m, 1)
                row[f"{m}_pct"] = round(100 * m_m / pop_m, 1) if pop_m else None
            w.writerow(row)

    # Console summary (Under40 view, same shape as the original script)
    world_pop = sum(totals["TotalPop"].values()) / 1000
    world_u40 = sum(totals["Under40"].values()) / 1000

    print(f"{'Region':<30}{'Countries':>10}{'Pop (M)':>12}"
          f"{'Under40 (M)':>14}{'%':>8}")
    for r in regions:
        pop_m = totals["TotalPop"][r] / 1000
        u40_m = totals["Under40"][r] / 1000
        print(f"{r:<30}{counts[r]:>10}{pop_m:>12,.0f}{u40_m:>14,.0f}"
              f"{100*u40_m/pop_m:>8.1f}")
    print("-" * 74)
    print(f"{'WORLD':<30}{sum(counts.values()):>10}{world_pop:>12,.0f}"
          f"{world_u40:>14,.0f}{100*world_u40/world_pop:>8.1f}")

    print(f"\nWrote {out_path} with columns for: "
          + ", ".join(METRICS))


if __name__ == "__main__":
    main()
