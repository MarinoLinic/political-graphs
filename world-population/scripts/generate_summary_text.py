"""
SCRIPT 3 of 3 — generate_summary_text.py

Takes region_summary.csv (script 2's output) and renders the bar-chart
style text block for every metric, e.g.:

    People under 40:

    [flag] South Asia ----------------- 1,362 million (27%)
    ...

    Source: UN World Population Prospects 2024, medium variant.

Percentages here are each region's SHARE OF THE WORLD TOTAL for that
metric (e.g. "South Asia has 27% of the world's under-40 population"),
which is different from the Region_pct column in region_summary.csv
(which is "% of South Asia's own population that is under 40").

Usage:
    python3 generate_summary_text.py [region_summary_csv]

Output:
    population_summary.md — all five metrics, each as its own block.
"""

import csv
import decimal
import sys

DEFAULT_SUMMARY_CSV = "region_summary.csv"

EMOJI = {
    "South Asia": "\U0001F1EE\U0001F1F3",                  # IN flag
    "Sub-Saharan Africa": "\U0001F30D",                      # globe Africa/Europe
    "Northeast Asia": "\U0001F1E8\U0001F1F3",                # CN flag
    "Middle East & North Africa": "\U0001F54C",              # mosque
    "Southeast Asia": "\U0001F1EE\U0001F1E9",                 # ID flag
    "Latin America & Caribbean": "\U0001F30E",                # globe Americas
    "Europe (incl. Russia)": "\U0001F1EA\U0001F1FA",          # EU flag
    "North America": "\U0001F1FA\U0001F1F8",                  # US flag
    "Central Asia": "\U0001F1FA\U0001F1FF",                   # UZ flag
    "Oceania & Australasia": "\U0001F1E6\U0001F1FA",          # AU flag
}

# metric key in region_summary.csv -> (section title, footnote)
METRICS = [
    ("TotalPop", "Total population:", None),
    ("Under40", "People under 40:", None),
    ("Under20", "People under 20:", None),
    ("Age0to4", "Children ages 0-4:", None),
    ("Over65", "People 65 and older:", None),
]

SOURCE_LINE = "Source: UN World Population Prospects 2024, medium variant."


def round_half_up(x, decimals=0):
    q = decimal.Decimal('1') if decimals == 0 else decimal.Decimal('0.' + '0' * decimals)
    d = decimal.Decimal(str(x)).quantize(q, rounding=decimal.ROUND_HALF_UP)
    return int(d) if decimals == 0 else float(d)


def format_pct(pct):
    if pct < 2:
        return f"{round_half_up(pct, 1)}%"
    return f"{round_half_up(pct)}%"


def build_block(metric, rows, world_total):
    # rows: list of (region, value_m) sorted descending by value
    formatted = []
    for region, value_m in rows:
        pct = 100 * value_m / world_total if world_total else 0
        val_str = f"{round_half_up(value_m):,}"
        formatted.append((region, val_str, format_pct(pct)))

    max_name_len = max(len(r[0]) for r in formatted)
    lines = []
    for region, val_str, pct_str in formatted:
        dashes = (max_name_len - len(region)) + 1
        if region == "Oceania & Australasia":
            dashes += 1
        emoji = EMOJI.get(region, "\U0001F4CD")
        lines.append(f"{emoji} {region} {'-' * dashes} {val_str} million ({pct_str})")
    return "\n".join(lines)


def main():
    summary_csv = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SUMMARY_CSV

    with open(summary_csv, newline="", encoding="utf-8") as f:
        data = list(csv.DictReader(f))

    blocks = []
    for metric, title, note in METRICS:
        rows = sorted(
            ((d["Region"], float(d[f"{metric}_M"])) for d in data),
            key=lambda x: x[1], reverse=True,
        )
        world_total = sum(v for _, v in rows)
        body = build_block(metric, rows, world_total)

        section = f"### {title}\n\n```\n{title}\n\n{body}\n\n{SOURCE_LINE}\n```"
        if note:
            section += f"\n\n*{note}*"
        blocks.append(section)

    out_path = "population_summary.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# World Population by Region — UN WPP2024 (2025)\n\n")
        f.write("\n\n".join(blocks))
        f.write("\n")

    print(f"Wrote {out_path} with {len(METRICS)} sections: "
          + ", ".join(m for m, _, _ in METRICS))


if __name__ == "__main__":
    main()
