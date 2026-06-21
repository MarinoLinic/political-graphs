"""
generate_charts.py — chart pack for the WPP2024 population pipeline.

Reads the CSVs produced by run_all.py (country_data_<year>.csv and
region_summary.csv in output/csv/) and renders a set of PNG charts into
output/images/. One script, no arguments needed for the common case.

USAGE:
    python3 scripts/generate_charts.py            # uses year 2025
    python3 scripts/generate_charts.py 2030        # uses a different year

CHARTS PRODUCED (output/images/):
    01_total_population_by_region.png       horizontal bar
    02_under40_by_region.png                horizontal bar
    03_under20_by_region.png                horizontal bar
    04_age0to4_by_region.png                horizontal bar
    05_over65_by_region.png                 horizontal bar
    06_population_treemap.png               proportional treemap
    07_population_share_donut.png           donut / pie
    08_age_structure_by_region.png          stacked bars (sorted by 0-4 share)
    09_share_comparison_under40.png         paired bars: region % of under-40 vs. total pop
    10_share_comparison_under20.png         paired bars: region % of under-20 vs. total pop
    11_share_comparison_age0to4.png         paired bars: region % of 0-4 vs. total pop
    12_share_comparison_over65.png          paired bars: region % of 65+ vs. total pop
    13_youth_share_vs_size_bubble.png       bubble chart: region size vs. % under 40
    14_world_map_under40_pct.png            choropleth: share under 40 (needs shapefile)
    15_world_map_under20_pct.png            choropleth: share under 20 (needs shapefile)
    16_world_map_age0to4_pct.png            choropleth: share ages 0-4 (needs shapefile)
    17_world_map_over65_pct.png             choropleth: share 65+ (needs shapefile)
    (The total-population choropleth is omitted — India/China dominate so
     completely that every other country washes out on a linear scale.)

WORLD MAP DATA:
    This script does NOT ship a basemap (license + file size). To get the
    choropleth charts, download a free Natural Earth countries shapefile
    and drop it into the project's data/world_map/ folder. Full
    instructions are in the big comment block at the bottom of this file
    — read that before asking "where do I get the map".
"""

import csv
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Rectangle

# ---------------------------------------------------------------------------
# Paths — anchored to the project root (this script lives in scripts/), so
# it doesn't matter what directory you launch python3 from.
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__ if "__file__" in dir() else os.path.abspath(sys.argv[0])))
# generate_charts.py lives in scripts/; the project root is one level up
BASE_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "scripts" else SCRIPT_DIR
CSV_DIR = os.path.join(BASE_DIR, "output", "csv")
IMG_DIR = os.path.join(BASE_DIR, "output", "images")
MAP_DIR = os.path.join(BASE_DIR, "data", "world_map")

os.makedirs(IMG_DIR, exist_ok=True)

YEAR = sys.argv[1] if len(sys.argv) > 1 else "2025"
COUNTRY_CSV = os.path.join(CSV_DIR, f"country_data_{YEAR}.csv")
REGION_CSV = os.path.join(CSV_DIR, "region_summary.csv")

# ---------------------------------------------------------------------------
# Shared visual identity (same family used elsewhere in this project)
# ---------------------------------------------------------------------------
PAGE_BG     = "#EAE3D8"
CARD_BG     = "#FCFAF6"
INK         = "#1E2B29"
MUTED       = "#7A766D"
ACCENT_WINE = "#7A2049"
ACCENT_TEAL = "#0B5C53"

CMAP = mcolors.LinearSegmentedColormap.from_list(
    "proj_seq", [ACCENT_WINE, "#E6A6BE", "#FBF6EF", "#8FD6C8", ACCENT_TEAL]
)


def fmt_m(v):
    """Format a millions value like 1992.8 -> '1,993M' or 47.0 -> '47M'."""
    return f"{round(v):,}M"


def load_region_summary():
    if not os.path.exists(REGION_CSV):
        sys.exit(
            f"*** Missing {REGION_CSV}\n"
            f"Run run_all.py first to generate the CSVs this script needs."
        )
    with open(REGION_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in list(r.items()):
            if k not in ("Region",):
                r[k] = float(v) if v not in (None, "") else 0.0
    rows.sort(key=lambda r: r["TotalPop_M"], reverse=True)
    return rows


def load_country_data():
    if not os.path.exists(COUNTRY_CSV):
        sys.exit(
            f"*** Missing {COUNTRY_CSV}\n"
            f"Run run_all.py first to generate the CSVs this script needs "
            f"(or pass a different year as an argument)."
        )
    with open(COUNTRY_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    numeric_suffixes = ("_thousands", "_pct")
    for r in rows:
        for k in list(r.keys()):
            if k.endswith(numeric_suffixes) and r[k] not in (None, ""):
                r[k] = float(r[k])
    return rows


# ---------------------------------------------------------------------------
# Card / title / footer helpers shared by every chart for a consistent look
# ---------------------------------------------------------------------------

def add_card(fig):
    card_ax = fig.add_axes((0, 0, 1, 1), zorder=0)
    card_ax.axis("off")
    card_ax.patch.set_alpha(0)
    card = FancyBboxPatch(
        (0.012, 0.012), 0.976, 0.976,
        boxstyle="round,pad=0,rounding_size=0.018",
        transform=card_ax.transAxes,
        facecolor=CARD_BG, edgecolor="none", zorder=0,
    )
    card.set_path_effects([pe.withSimplePatchShadow(offset=(0, -3), alpha=0.18, shadow_rgbFace="#000000")])
    card_ax.add_patch(card)


def add_titles(ax, title, subtitle):
    ax.text(0.0, 1.12, title, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=17, fontweight="bold", color=INK)
    ax.text(0.0, 1.045, subtitle, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=10.5, fontweight="medium", color=ACCENT_TEAL)


def add_footer(fig, ax_left, fig_h_in, source_h_in, line1):
    fig.text(ax_left, source_h_in / fig_h_in * 0.78, line1,
              ha="left", va="center", fontsize=7, color=MUTED)


def new_figure(chart_w_in, chart_h_in, title_h_in=1.05, source_h_in=0.60,
               left_margin_in=0.35, right_margin_in=0.45):
    fig_w = left_margin_in + chart_w_in + right_margin_in
    fig_h = title_h_in + chart_h_in + source_h_in
    fig = plt.figure(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(PAGE_BG)
    add_card(fig)
    ax_left = left_margin_in / fig_w
    ax_bottom = source_h_in / fig_h
    ax_width = chart_w_in / fig_w
    ax_height = chart_h_in / fig_h
    ax = fig.add_axes((ax_left, ax_bottom, ax_width, ax_height), zorder=2)
    ax.set_facecolor(CARD_BG)
    return fig, ax, ax_left, fig_h, source_h_in


def save(fig, name):
    out_path = os.path.join(IMG_DIR, name)
    plt.savefig(out_path, dpi=400, bbox_inches="tight", pad_inches=0.22, facecolor=PAGE_BG)
    plt.close(fig)
    print("Saved:", out_path)


# ===========================================================================
# CHARTS 01-05: ranked horizontal bar, one per metric
# ===========================================================================
BAR_METRICS = [
    ("01_total_population_by_region.png", "TotalPop_M", "Total Population by Region",
     f"All ages · {YEAR} estimates"),
    ("02_under40_by_region.png", "Under40_M", "People Under 40, by Region",
     f"Ages 0-39 · {YEAR} estimates"),
    ("03_under20_by_region.png", "Under20_M", "People Under 20, by Region",
     f"Ages 0-19 · {YEAR} estimates"),
    ("04_age0to4_by_region.png", "Age0to4_M", "Children Ages 0-4, by Region",
     f"{YEAR} estimates"),
    ("05_over65_by_region.png", "Over65_M", "People 65 and Older, by Region",
     f"{YEAR} estimates"),
]


def chart_ranked_bar(rows, value_key, filename, title, subtitle):
    data = sorted(rows, key=lambda r: r[value_key], reverse=True)
    names = [r["Region"] for r in data]
    vals = [r[value_key] for r in data]
    vmax = max(vals) if vals else 1
    norm = mcolors.Normalize(vmin=0, vmax=vmax)

    fig, ax, ax_left, fig_h, source_h = new_figure(8.6, 5.4)
    y_pos = list(range(len(data)))[::-1]
    bar_h = 0.62
    for y, name, v in zip(y_pos, names, vals):
        color = CMAP(norm(v))
        ax.add_patch(FancyBboxPatch((0, y - bar_h / 2), v, bar_h,
                                     boxstyle="round,pad=0,rounding_size=0.18",
                                     facecolor=color, edgecolor="none", zorder=3))
        ax.text(-vmax * 0.02, y, name, ha="right", va="center",
                fontsize=10.5, fontweight="bold", color=INK, zorder=4)
        lum = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        chip_color = ACCENT_TEAL if lum < 0.6 else ACCENT_WINE
        t = ax.text(v + vmax * 0.02, y, fmt_m(v), ha="left", va="center", fontsize=10,
                    fontweight="bold", color="white", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.32,rounding_size=0.35",
                              facecolor=chip_color, edgecolor="none", alpha=0.96))
        bbox_patch = t.get_bbox_patch()
        if bbox_patch is not None:
            bbox_patch.set_path_effects(
                [pe.withSimplePatchShadow(offset=(1.2, -1.4), alpha=0.25, shadow_rgbFace="#000000")]
            )

    ax.set_xlim(-vmax * 0.62, vmax * 1.22)
    ax.set_ylim(-0.7, len(data) - 0.3)
    ax.axis("off")
    add_titles(ax, title, subtitle)
    add_footer(fig, ax_left, fig_h, source_h,
               "Source: UN World Population Prospects 2024, medium variant.")
    save(fig, filename)


# ===========================================================================
# CHART 06: treemap
# ===========================================================================

def squarify(values, x, y, w, h):
    if not values:
        return []
    total = sum(values)

    def worst_ratio(row, length):
        s = sum(row)
        if s == 0:
            return float("inf")
        side = s / length
        return max(
            max(side / (v / side) if v else float("inf"), (v / side) / side if v else float("inf"))
            for v in row
        )

    rects = []

    def layout(vals, x, y, w, h):
        vals = list(vals)
        while vals:
            length = min(w, h)
            row = [vals[0]]
            best_ratio = worst_ratio(row, length)
            i = 1
            while i < len(vals):
                trial = row + [vals[i]]
                r = worst_ratio(trial, length)
                if r <= best_ratio:
                    row, best_ratio = trial, r
                    i += 1
                else:
                    break
            row_sum = sum(row)
            if w >= h:
                row_w = row_sum / h
                cy = y
                for v in row:
                    rh = v / row_w if row_w else 0
                    rects.append((x, cy, row_w, rh))
                    cy += rh
                x += row_w
                w -= row_w
            else:
                row_h = row_sum / w
                cx = x
                for v in row:
                    rw = v / row_h if row_h else 0
                    rects.append((cx, y, rw, row_h))
                    cx += rw
                y += row_h
                h -= row_h
            vals = vals[len(row):]

    scale = (w * h) / total
    layout([v * scale for v in values], x, y, w, h)
    return rects


def chart_treemap(rows):
    data = sorted(rows, key=lambda r: r["TotalPop_M"], reverse=True)
    names = [r["Region"] for r in data]
    vals = [r["TotalPop_M"] for r in data]
    vmax = max(vals)
    norm = mcolors.Normalize(vmin=0, vmax=vmax)

    fig, ax, ax_left, fig_h, source_h = new_figure(9.0, 5.4, source_h_in=0.72,
                                                     left_margin_in=0.30, right_margin_in=0.30)
    rects = squarify(vals, 0, 0, 100, 60)
    for (x, y, w, h), name, v in zip(rects, names, vals):
        color = CMAP(norm(v))
        pad = 0.35
        ax.add_patch(Rectangle((x + pad, y + pad), max(w - 2 * pad, 0.1), max(h - 2 * pad, 0.1),
                                facecolor=color, edgecolor=CARD_BG, linewidth=2.2, zorder=3))
        lum = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        txt_color = "white" if lum < 0.55 else "#14201F"
        outline = "#102422" if lum < 0.55 else "#F4F1EA"
        cx, cy = x + w / 2, y + h / 2
        area = w * h
        if area > 18 and min(w, h) > 4.0:
            fs_name = 11 if area > 60 else 9
            t1 = ax.text(cx, cy + h * 0.14, name, ha="center", va="center",
                         fontsize=fs_name, fontweight="bold", color=txt_color, zorder=5)
            t1.set_path_effects([pe.withStroke(linewidth=2.0, foreground=outline, alpha=0.9)])
            chip_color = ACCENT_TEAL if v >= vmax * 0.3 else ACCENT_WINE
            ax.text(cx, cy - h * 0.16, fmt_m(v), ha="center", va="center",
                    fontsize=10.5, fontweight="bold", color="white", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.3,rounding_size=0.35",
                              facecolor=chip_color, edgecolor="none", alpha=0.95))
        elif area > 2:
            ax.text(cx, cy, "\u2022", ha="center", va="center", fontsize=14, color=txt_color, zorder=5)

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.set_aspect("equal")
    ax.axis("off")
    add_titles(ax, "World Population, by Region — Proportional View",
               f"Area = share of world total · {YEAR} estimates")
    add_footer(fig, ax_left, fig_h, source_h,
               "Source: UN World Population Prospects 2024, medium variant.")
    save(fig, "06_population_treemap.png")


# ===========================================================================
# CHART 07: donut
# ===========================================================================

def chart_donut(rows):
    data = sorted(rows, key=lambda r: r["TotalPop_M"], reverse=True)
    names = [r["Region"] for r in data]
    vals = [r["TotalPop_M"] for r in data]
    total = sum(vals)
    vmax = max(vals)
    norm = mcolors.Normalize(vmin=0, vmax=vmax)
    colors = [CMAP(norm(v)) for v in vals]

    fig, ax, ax_left, fig_h, source_h = new_figure(6.6, 5.6, left_margin_in=0.35, right_margin_in=2.6)
    pie_result = ax.pie(vals, colors=colors, startangle=90, counterclock=False,
                        wedgeprops=dict(width=0.42, edgecolor=CARD_BG, linewidth=2.5))
    wedges = pie_result[0]
    ax.text(0, 0.06, f"{total:,.0f}M", ha="center", va="center",
            fontsize=20, fontweight="bold", color=INK)
    ax.text(0, -0.14, f"world population, {YEAR}", ha="center", va="center",
            fontsize=9, color=MUTED)
    ax.set_aspect("equal")

    legend_labels = [f"{n} — {v/total*100:.0f}%" for n, v in zip(names, vals)]
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1.05, 0.5),
              frameon=False, fontsize=9.5, labelcolor=INK, handlelength=1.1)

    add_titles(ax, "Share of World Population, by Region", f"{YEAR} estimates")
    add_footer(fig, ax_left, fig_h, source_h,
               "Source: UN World Population Prospects 2024, medium variant.")
    save(fig, "07_population_share_donut.png")


# ===========================================================================
# CHART 08: age-structure stacked bars (0-19 / 20-39 / 40-64 / 65+)
# ===========================================================================

def chart_age_structure(rows):
    data = sorted(rows, key=lambda r: r["Age0to4_pct"], reverse=True)
    names = [r["Region"] for r in data]

    seg_0_19 = [r["Under20_pct"] for r in data]
    seg_20_39 = [r["Under40_pct"] - r["Under20_pct"] for r in data]
    seg_65p = [r["Over65_pct"] for r in data]
    seg_40_64 = [100 - r["Under40_pct"] - r["Over65_pct"] for r in data]

    seg_colors = ["#8FD6C8", ACCENT_TEAL, "#D8B0A0", ACCENT_WINE]
    seg_labels = ["0-19", "20-39", "40-64", "65+"]
    segments = [seg_0_19, seg_20_39, seg_40_64, seg_65p]

    fig, ax, ax_left, fig_h, source_h = new_figure(8.6, 5.6)
    y_pos = list(range(len(data)))[::-1]
    bar_h = 0.6
    for y, name in zip(y_pos, names):
        left = 0
        idx = names.index(name)
        for seg_vals, color in zip(segments, seg_colors):
            v = seg_vals[idx]
            ax.add_patch(Rectangle((left, y - bar_h / 2), v, bar_h,
                                    facecolor=color, edgecolor=CARD_BG, linewidth=1.0, zorder=3))
            if v > 5:
                lum = 0.299 * mcolors.to_rgb(color)[0] + 0.587 * mcolors.to_rgb(color)[1] + 0.114 * mcolors.to_rgb(color)[2]
                txt_c = "white" if lum < 0.55 else "#14201F"
                ax.text(left + v / 2, y, f"{v:.0f}%", ha="center", va="center",
                        fontsize=8.5, fontweight="bold", color=txt_c, zorder=4)
            left += v
        ax.text(-2, y, name, ha="right", va="center",
                fontsize=10, fontweight="bold", color=INK, zorder=4)

    ax.set_xlim(-58, 102)
    ax.set_ylim(-0.7, len(data) - 0.3)
    ax.axis("off")

    handles = [Rectangle((0, 0), 1, 1, facecolor=c) for c in seg_colors]
    ax.legend(handles, seg_labels, loc="upper center", bbox_to_anchor=(0.5, -0.03),
              ncol=4, frameon=False, fontsize=9.5, labelcolor=INK, handlelength=1.2)

    add_titles(ax, "Age Structure by Region", f"Share of regional population by age band · {YEAR} estimates")
    add_footer(fig, ax_left, fig_h, source_h,
               "Source: UN World Population Prospects 2024, medium variant.")
    save(fig, "08_age_structure_by_region.png")


# ===========================================================================
# CHARTS 09-12: demographic share vs. total population share — paired bars
#
# For each age metric, each region gets two side-by-side bars:
#   - its share of the TOTAL world population (grey reference bar)
#   - its share of THAT demographic globally (coloured bar)
# Sorted by demographic share descending so the most over-represented
# regions rise to the top.
# ===========================================================================

SHARE_METRICS = [
    ("09_share_comparison_under40.png",
     "Under40_M",  "TotalPop_M",
     "Regional Share: Under-40 vs. Total Population",
     f"Each region's % of world under-40 population vs. its % of world total · {YEAR}"),
    ("10_share_comparison_under20.png",
     "Under20_M",  "TotalPop_M",
     "Regional Share: Under-20 vs. Total Population",
     f"Each region's % of world under-20 population vs. its % of world total · {YEAR}"),
    ("11_share_comparison_age0to4.png",
     "Age0to4_M",  "TotalPop_M",
     "Regional Share: Ages 0-4 vs. Total Population",
     f"Each region's % of world 0-4 population vs. its % of world total · {YEAR}"),
    ("12_share_comparison_over65.png",
     "Over65_M",   "TotalPop_M",
     "Regional Share: 65+ vs. Total Population",
     f"Each region's % of world 65+ population vs. its % of world total · {YEAR}"),
]

# Visual treatment for the two bar types
_COL_DEMO  = ACCENT_TEAL   # coloured bar = demographic share
_COL_TOTAL = "#C8C2B6"     # neutral grey  = total pop share


def chart_share_comparison(rows, demo_key, total_key, filename, title, subtitle):
    world_demo  = sum(r[demo_key]  for r in rows)
    world_total = sum(r[total_key] for r in rows)

    # Build (region, demo_share, total_share) and sort by demo share desc
    data = sorted(
        [
            (r["Region"],
             r[demo_key]  / world_demo  * 100 if world_demo  else 0,
             r[total_key] / world_total * 100 if world_total else 0)
            for r in rows
        ],
        key=lambda t: t[1], reverse=True,
    )

    n = len(data)
    # Each region gets two bars; add a small gap between region groups
    bar_h   = 0.30   # height of each individual bar
    gap     = 0.18   # gap between the two bars within a group
    stride  = 1.0    # vertical distance between group centres

    fig, ax, ax_left, fig_h, source_h = new_figure(8.6, n * stride + 0.4,
                                                     left_margin_in=0.35,
                                                     right_margin_in=0.55)
    vmax = max(max(ds, ts) for _, ds, ts in data) * 1.0

    for i, (name, demo_share, total_share) in enumerate(data):
        y_centre = (n - 1 - i) * stride   # top region at the top

        y_demo  = y_centre + gap / 2
        y_total = y_centre - gap / 2 - bar_h

        # Demographic bar (coloured)
        ax.add_patch(FancyBboxPatch(
            (0, y_demo), demo_share, bar_h,
            boxstyle="round,pad=0,rounding_size=0.10",
            facecolor=_COL_DEMO, edgecolor="none", zorder=3))
        ax.text(demo_share + vmax * 0.015, y_demo + bar_h / 2,
                f"{demo_share:.1f}%", va="center", ha="left",
                fontsize=8.5, fontweight="bold", color=_COL_DEMO, zorder=4)

        # Total-population bar (grey reference)
        ax.add_patch(FancyBboxPatch(
            (0, y_total), total_share, bar_h,
            boxstyle="round,pad=0,rounding_size=0.10",
            facecolor=_COL_TOTAL, edgecolor="none", zorder=3))
        ax.text(total_share + vmax * 0.015, y_total + bar_h / 2,
                f"{total_share:.1f}%", va="center", ha="left",
                fontsize=8.5, color=MUTED, zorder=4)

        # Region label to the left, centred on the group
        ax.text(-vmax * 0.02, y_centre + (bar_h - gap) / 2,
                name, ha="right", va="center",
                fontsize=9.5, fontweight="bold", color=INK, zorder=4)

    ax.set_xlim(-vmax * 0.58, vmax * 1.22)
    ax.set_ylim(-stride * 0.6, (n - 1) * stride + stride * 0.6)
    ax.axis("off")

    # Legend
    from matplotlib.patches import Patch
    handles = [
        Patch(facecolor=_COL_DEMO,  label="Share of demographic"),
        Patch(facecolor=_COL_TOTAL, label="Share of world population"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.03),
              ncol=2, frameon=False, fontsize=9, labelcolor=INK, handlelength=1.2)

    add_titles(ax, title, subtitle)
    add_footer(fig, ax_left, fig_h, source_h,
               "Source: UN World Population Prospects 2024, medium variant.")
    save(fig, filename)


# ===========================================================================
# CHART 13: bubble chart — region size vs. youth share
# ===========================================================================

def chart_bubble(rows):
    data = rows
    fig, ax, ax_left, fig_h, source_h = new_figure(8.6, 5.8, left_margin_in=0.6)
    vmax = max(r["TotalPop_M"] for r in data)
    for r in data:
        x = r["Under40_pct"]
        y = r["TotalPop_M"]
        size = 200 + 1800 * (y / vmax)
        color = CMAP(mcolors.Normalize(0, vmax)(y))
        ax.scatter([x], [y], s=size, color=color, edgecolor=CARD_BG, linewidth=1.6, zorder=3, alpha=0.92)
        ax.annotate(r["Region"], (x, y), xytext=(0, 0),
                    textcoords="offset points", ha="center", va="center",
                    fontsize=8.5, fontweight="bold", color=INK, zorder=4)

    ax.set_xlabel("Share of region's population under 40 (%)", fontsize=10, color=MUTED)
    ax.set_ylabel("Total population (M)", fontsize=10, color=MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#D8D2C4")
    ax.grid(axis="both", color="#E6E0D2", linewidth=0.6, linestyle="--", zorder=0)
    ax.set_xlim(35, 90)
    ax.set_ylim(-80, max(r["TotalPop_M"] for r in data) * 1.18)

    add_titles(ax, "Youth Share vs. Population Size, by Region",
               f"Bubble size = total population · {YEAR} estimates")
    add_footer(fig, ax_left, fig_h, source_h,
               "Source: UN World Population Prospects 2024, medium variant.")
    save(fig, "13_youth_share_vs_size_bubble.png")


# ===========================================================================
# CHARTS 11-15: world map choropleths — age-share metrics (optional — needs a shapefile)
# Each map shows one age-band's share of each country's population.
# The total-population choropleth is intentionally omitted: India and China
# dominate so completely that every other country washes out.
# ===========================================================================

MAP_METRICS = [
    ("Under40_pct",   "14_world_map_under40_pct.png",
     "Share of Population Under 40, by Country",   f"{YEAR} estimates, %"),
    ("Under20_pct",   "15_world_map_under20_pct.png",
     "Share of Population Under 20, by Country",   f"{YEAR} estimates, %"),
    ("Age0to4_pct",   "16_world_map_age0to4_pct.png",
     "Share of Population Ages 0-4, by Country",   f"{YEAR} estimates, %"),
    ("Over65_pct",    "17_world_map_over65_pct.png",
     "Share of Population 65+, by Country",        f"{YEAR} estimates, %"),
]


def chart_world_maps(country_rows):
    shp_candidates = []
    if os.path.isdir(MAP_DIR):
        for fn in os.listdir(MAP_DIR):
            if fn.lower().endswith(".shp"):
                shp_candidates.append(os.path.join(MAP_DIR, fn))

    if not shp_candidates:
        print(f"\n[skip] No .shp file found in {MAP_DIR} — skipping the world map "
              f"charts (14-17). See the instructions at the bottom of "
              f"generate_charts.py for where to download one.")
        return

    try:
        import geopandas as gpd
    except ImportError:
        print("\n[skip] geopandas is not installed, so the world map charts "
              "(14-17) were skipped. Install it with:\n"
              "    pip install geopandas --break-system-packages")
        return

    shp_path = shp_candidates[0]
    world = gpd.read_file(shp_path)

    iso_col = None
    for candidate in ("ISO_A3", "ISO_A3_EH", "ADM0_A3", "ISO3", "iso_a3"):
        if candidate in world.columns:
            iso_col = candidate
            break
    if iso_col is None:
        print(f"\n[skip] Couldn't find an ISO3 country-code column in {shp_path} "
              f"(looked for ISO_A3 / ISO_A3_EH / ADM0_A3 / ISO3). Charts 14-17 skipped.")
        return

    by_iso3 = {r["ISO3"]: r for r in country_rows}

    # Attach all age-share columns to the geodataframe up front
    for col, _, _, _ in MAP_METRICS:
        world[col] = world[iso_col].map(
            lambda code, c=col: by_iso3[code][c] if code in by_iso3 else None)

    SOURCE = "Source: UN World Population Prospects 2024, medium variant."

    def draw_map(column, filename, title, subtitle):
        fig_w, fig_h = 13.0, 7.2
        fig = plt.figure(figsize=(fig_w, fig_h))
        fig.patch.set_facecolor(PAGE_BG)
        add_card(fig)
        ax = fig.add_axes((0.03, 0.10, 0.94, 0.78))
        ax.set_facecolor(CARD_BG)

        world.plot(column=column, cmap=CMAP, linewidth=0.3, edgecolor="#FFFFFF",
                   ax=ax, missing_kwds={"color": "#DDD6C8", "label": "No data"})
        ax.set_axis_off()
        ax.set_xlim(-180, 180)
        ax.set_ylim(-60, 85)

        sm = plt.cm.ScalarMappable(
            cmap=CMAP,
            norm=mcolors.Normalize(vmin=world[column].min(), vmax=world[column].max()))
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation="horizontal",
                            fraction=0.04, pad=0.02, shrink=0.4)
        cbar.ax.tick_params(labelsize=8, colors=MUTED)
        cbar.outline.set_visible(False)  # type: ignore[union-attr]

        fig.text(0.04, 0.94, title, fontsize=17, fontweight="bold", color=INK)
        fig.text(0.04, 0.90, subtitle, fontsize=10.5, color=ACCENT_TEAL)
        fig.text(0.04, 0.035, SOURCE, fontsize=7, color=MUTED)

        out_path = os.path.join(IMG_DIR, filename)
        plt.savefig(out_path, dpi=350, facecolor=PAGE_BG)
        plt.close(fig)
        print("Saved:", out_path)

    for column, filename, title, subtitle in MAP_METRICS:
        draw_map(column, filename, title, subtitle)


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    region_rows = load_region_summary()
    country_rows = load_country_data()

    for filename, key, title, subtitle in BAR_METRICS:
        chart_ranked_bar(region_rows, key, filename, title, subtitle)

    chart_treemap(region_rows)
    chart_donut(region_rows)
    chart_age_structure(region_rows)

    for filename, demo_key, total_key, title, subtitle in SHARE_METRICS:
        chart_share_comparison(region_rows, demo_key, total_key, filename, title, subtitle)

    chart_bubble(region_rows)
    chart_world_maps(country_rows)

    print(f"\nAll charts written to: {IMG_DIR}")


if __name__ == "__main__":
    main()


# ===========================================================================
# WHERE TO GET THE WORLD MAP (for charts 11 and 12)
# ===========================================================================
#
# This project uses Natural Earth's free, public-domain country boundaries.
# No API key, no license restrictions, no attribution legally required
# (though it's good practice).
#
# 1. Go to:
#       https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/
#    and click "Download countries" (this is the 1:110m scale — small file,
#    plenty of detail for a world choropleth). If that link ever moves,
#    search "Natural Earth 110m admin 0 countries".
#
#    Direct file (same data, hosted on AWS, sometimes easier to reach):
#       https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip
#
# 2. Unzip it. You'll get a handful of files that all start with
#    "ne_110m_admin_0_countries" (.shp, .shx, .dbf, .prj, .cpg, ...).
#    A shapefile is NOT just the .shp — geopandas needs the .shx and .dbf
#    sitting right next to it, so unzip everything, don't cherry-pick.
#
# 3. Put all of those files into this project's:
#       data/world_map/
#    (create that folder if it doesn't exist yet).
#
# 4. Re-run this script. It auto-detects the .shp file in data/world_map/
#    and adds charts 11 and 12. If it's missing, those two are just
#    skipped with a printed note — nothing else breaks.
#
# Want more detail (e.g. for zooming into a specific region)? Natural
# Earth also publishes a 1:50m and 1:10m version at the same URL pattern
# (50m_cultural / 10m_cultural instead of 110m_cultural) — bigger files,
# more coastline/border detail.
# ===========================================================================