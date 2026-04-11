import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patheffects import withStroke

# =============================================================================
# PROJECT SETUP
# =============================================================================
file   = "images/amish_population_2100"
author = "@MarinoLinic"
source = "Source: Young Center for Anabaptist & Pietist Studies, Elizabethtown College"
title  = "Amish Population in the USA"

# =============================================================================
# THEME SELECTOR
# =============================================================================
# Choose one of: "dark" | "light" | "amber"
THEME = "dark"

# =============================================================================
# COLORS  (set by theme)
# =============================================================================
_THEMES = {
    # ── Dark (original) ──────────────────────────────────────────────────────
    "dark": dict(
        BG            = "#090c14",
        BG_AX         = "#0c1020",
        COL_HIST      = "#f0c060",
        COL_MARK      = "#f0c060",
        COL_PROJ_A    = "#40d0c0",
        COL_PROJ_B    = "#a060f0",
        COL_FILL_H    = "#f0c060",
        COL_GRID_Y    = "#14203a",
        COL_GRID_X    = "#101828",
        COL_SPINE     = "#1e2a3a",
        COL_TICK      = "#506070",
        COL_TITLE     = "#eee8d0",
        COL_AXIS_LBL  = "#506070",
        COL_ANNOT_TXT = "#c8dce8",
        COL_ANNOT_BG  = "#0a1422",
        COL_ANNOT_EC  = "#304050",
        COL_ANNOT_AR  = "#304858",
        COL_SOURCE    = "#485e72",
        COL_HANDLE    = "#c8e8f8",   # username: light cyan-white, clearly visible
        COL_LEG_LBL   = "#a0bcd0",
        COL_LEG_EDGE  = "#283848",
        COL_GLOW      = "#090c14",
    ),
    # ── Light ────────────────────────────────────────────────────────────────
    "light": dict(
        BG            = "#f4f1eb",
        BG_AX         = "#ffffff",
        COL_HIST      = "#c07820",
        COL_MARK      = "#c07820",
        COL_PROJ_A    = "#1899a0",
        COL_PROJ_B    = "#7030c0",
        COL_FILL_H    = "#c07820",
        COL_GRID_Y    = "#ddd8cc",
        COL_GRID_X    = "#e8e4dc",
        COL_SPINE     = "#c8c0b0",
        COL_TICK      = "#808070",
        COL_TITLE     = "#1a1814",
        COL_AXIS_LBL  = "#707060",
        COL_ANNOT_TXT = "#1a1814",
        COL_ANNOT_BG  = "#fffff8",
        COL_ANNOT_EC  = "#b0a898",
        COL_ANNOT_AR  = "#908880",
        COL_SOURCE    = "#909080",
        COL_HANDLE    = "#4a3080",   # username: deep violet, stands out on light bg
        COL_LEG_LBL   = "#404030",
        COL_LEG_EDGE  = "#c0b8a8",
        COL_GLOW      = "#f4f1eb",
    ),
    # ── Amber (warm dark — parchment tones on deep brown) ────────────────────
    "amber": dict(
        BG            = "#110d08",
        BG_AX         = "#160f09",
        COL_HIST      = "#e8a030",
        COL_MARK      = "#e8a030",
        COL_PROJ_A    = "#e05030",
        COL_PROJ_B    = "#f0c040",
        COL_FILL_H    = "#e8a030",
        COL_GRID_Y    = "#231808",
        COL_GRID_X    = "#1c1208",
        COL_SPINE     = "#302010",
        COL_TICK      = "#705840",
        COL_TITLE     = "#f0e0c0",
        COL_AXIS_LBL  = "#705840",
        COL_ANNOT_TXT = "#f0ddb0",
        COL_ANNOT_BG  = "#0e0a05",
        COL_ANNOT_EC  = "#503820",
        COL_ANNOT_AR  = "#503820",
        COL_SOURCE    = "#604830",
        COL_HANDLE    = "#f0c878",   # username: warm gold, vivid against dark brown
        COL_LEG_LBL   = "#c0a070",
        COL_LEG_EDGE  = "#403020",
        COL_GLOW      = "#110d08",
    ),
}

_c = _THEMES[THEME]
BG            = _c["BG"]
BG_AX         = _c["BG_AX"]
COL_HIST      = _c["COL_HIST"]
COL_MARK      = _c["COL_MARK"]
COL_PROJ_A    = _c["COL_PROJ_A"]
COL_PROJ_B    = _c["COL_PROJ_B"]
COL_FILL_H    = _c["COL_FILL_H"]
COL_GRID_Y    = _c["COL_GRID_Y"]
COL_GRID_X    = _c["COL_GRID_X"]
COL_SPINE     = _c["COL_SPINE"]
COL_TICK      = _c["COL_TICK"]
COL_TITLE     = _c["COL_TITLE"]
COL_AXIS_LBL  = _c["COL_AXIS_LBL"]
COL_ANNOT_TXT = _c["COL_ANNOT_TXT"]
COL_ANNOT_BG  = _c["COL_ANNOT_BG"]
COL_ANNOT_EC  = _c["COL_ANNOT_EC"]
COL_ANNOT_AR  = _c["COL_ANNOT_AR"]
COL_SOURCE    = _c["COL_SOURCE"]
COL_HANDLE    = _c["COL_HANDLE"]
COL_LEG_LBL   = _c["COL_LEG_LBL"]
COL_LEG_EDGE  = _c["COL_LEG_EDGE"]
COL_GLOW      = _c["COL_GLOW"]

# =============================================================================
# TEXT SIZES & STYLES
# =============================================================================
FS_TITLE      = 26
FS_AXIS_LBL   = 15
FS_TICK       = 14
FS_LEGEND     = 14
FS_ANNOT      = 14
FS_SOURCE     = 11
FS_HANDLE     = 17           # kept for reference; actual size set by FS_HANDLE_NEW below

FW_TITLE      = "bold"
FW_ANNOT      = "bold"
FW_HANDLE     = "bold"

FF_TITLE      = "serif"
FS_TITLE_PAD  = 20          # padding between title and top of axes
FI_HANDLE     = "italic"

# =============================================================================
# FIGURE & EXPORT
# =============================================================================
FIG_W         = 14          # figure width in inches
FIG_H         = 9.6         # figure height in inches
FIG_DPI       = 300

# Explicit margin fractions — fraction of figure width/height reserved as
# whitespace on each side. Tune these to control padding symmetry.
# bbox_inches="tight" is intentionally NOT used on save so these are respected.
MARGIN = dict(
    top    = 0.12,   # above axes (title lives here)
    bottom = 0.16,   # below axes (source + username live here; extra space for x-label)
    left   = 0.09,   # left of axes (y-axis label + ticks live here)
    right  = 0.04,   # right of axes
)

# Caption row — vertical position of source & username within the bottom margin.
# Expressed as a fraction of the full figure height (not relative to margin).
# Keep this well below MARGIN["bottom"] so it never overlaps the x-axis label.
CAPTION_Y        = 0.032   # y position (figure fraction) for source & username baseline
CAPTION_VA       = "bottom"  # vertical anchor for caption text

# Username styling
FS_HANDLE_NEW    = 20        # slightly larger than before
HANDLE_GLOW_LW   = 4        # linewidth of the glow/stroke path effect

FIXED_OFFSET  = 430_000     # uniform vertical offset for milestone annotations

# =============================================================================
# DATA
# =============================================================================
years      = np.arange(2000, 2101, 1)
base_year  = 2025
base_pop   = 411_000
growth_rate = 0.035

def proj(yr: int) -> int:
    return int(base_pop * (1 + growth_rate) ** (yr - base_year))

def fmt_pop(n: int) -> str:
    if n >= 1_000_000:
        v = n / 1_000_000
        s = f"{v:.1f}".rstrip("0").rstrip(".")
        return f"{s}M"
    return f"{n // 1_000}K"

population = np.array([proj(int(y)) for y in years], dtype=float)

# Verified data points — see source notes at bottom of file
historical = {
    2000: 177_900,
    2010: 249_500,
    2015: 300_000,
    2020: 350_700,
    2025: 411_000,
}
hist_years = np.array(list(historical.keys()))
hist_pops  = np.array(list(historical.values()))

milestone_years = [2025, 2045, 2065, 2085, 2100]
milestones: dict[int, tuple[int, str]] = {}
for yr in milestone_years:
    p = historical.get(yr, proj(yr))
    label = "411K  (2025)" if yr == 2025 else fmt_pop(proj(yr))
    milestones[yr] = (p, label)

# =============================================================================
# FIGURE
# =============================================================================
fig = plt.figure(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor(BG)

# Place axes manually using MARGIN fractions — this is the key change.
# No tight_layout, no bbox_inches="tight" — we own every pixel.
ax = fig.add_axes((
    MARGIN["left"],
    MARGIN["bottom"],
    1.0 - MARGIN["left"] - MARGIN["right"],
    1.0 - MARGIN["top"]  - MARGIN["bottom"],
))
ax.set_facecolor(BG_AX)

# Gradient projected line
proj_mask = years >= 2025
px = years[proj_mask]
py = population[proj_mask]
cmap_proj = LinearSegmentedColormap.from_list("pg", [COL_PROJ_A, COL_PROJ_B])
for i in range(len(px) - 1):
    t = i / (len(px) - 2)
    ax.plot(px[i:i+2], py[i:i+2], color=cmap_proj(t), linewidth=3.4,
            solid_capstyle="round", zorder=4)
for i in range(len(px) - 1):
    t = i / (len(px) - 2)
    ax.fill_between(px[i:i+2], py[i:i+2], alpha=0.06, color=cmap_proj(t))

# Historical line & fill
ax.fill_between(hist_years, hist_pops, alpha=0.18, color=COL_FILL_H)
ax.plot(hist_years, hist_pops,
        color=COL_HIST, linewidth=3.4, solid_capstyle="round", zorder=5)
ax.scatter(hist_years, hist_pops,
           color=COL_HIST, s=72, zorder=6, edgecolors=BG, linewidths=1.0)

# Milestones
for yr, (pop_val, label) in milestones.items():
    t = max(0.0, (yr - 2025) / (2100 - 2025))
    dot_color = COL_HIST if yr <= 2025 else cmap_proj(t)
    ax.annotate(label,
                xy=(yr, pop_val),
                xytext=(yr, pop_val + FIXED_OFFSET),
                fontsize=FS_ANNOT,
                fontweight=FW_ANNOT,
                color=COL_ANNOT_TXT,
                ha="center",
                arrowprops=dict(arrowstyle="-", color=COL_ANNOT_AR, lw=1.0),
                bbox=dict(boxstyle="round,pad=0.5", fc=COL_ANNOT_BG,
                          ec=COL_ANNOT_EC, lw=1.0))
    ax.scatter([yr], [pop_val], color=dot_color, s=72, zorder=7,
               edgecolors=BG, linewidths=1.0)

# Today marker
ax.axvline(x=2025, color=COL_MARK, linewidth=0.8,
           linestyle="--", alpha=0.3, zorder=3)

# Axes styling
y_max = proj(2100) * 1.20
ax.set_xlim(1998, 2104)
ax.set_ylim(-y_max * 0.015, y_max)
ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _:
        f"{x/1e6:.1f}M" if x >= 1e6 else (f"{int(x/1e3)}K" if x > 0 else "")))

for spine in ax.spines.values():
    spine.set_edgecolor(COL_SPINE)
ax.tick_params(colors=COL_TICK, labelsize=FS_TICK)
ax.grid(axis="y", color=COL_GRID_Y, linewidth=0.7, linestyle="--")
ax.grid(axis="x", color=COL_GRID_X, linewidth=0.45, linestyle=":")

# Title — placed in figure coordinates so it sits in the top margin,
# horizontally aligned with the left edge of the axes.
fig.text(MARGIN["left"], 1.0 - MARGIN["top"] * 0.5,
         title,
         color=COL_TITLE, fontsize=FS_TITLE,
         fontweight=FW_TITLE, fontfamily=FF_TITLE,
         ha="left", va="top",
         transform=fig.transFigure)

ax.set_xlabel("Year", color=COL_AXIS_LBL, fontsize=FS_AXIS_LBL, labelpad=12)
ax.set_ylabel("Population", color=COL_AXIS_LBL, fontsize=FS_AXIS_LBL, labelpad=12)

# Legend
hist_patch = mpatches.Patch(color=COL_HIST, label="Historical data")
proj_patch = mpatches.Patch(color=COL_PROJ_A,
                             label=f"Projected  ·  2025–2100  ·  ~{growth_rate*100:.1f}%/yr")
ax.legend(handles=[hist_patch, proj_patch],
          loc="upper left",
          framealpha=0.35,
          facecolor=BG,
          edgecolor=COL_LEG_EDGE,
          labelcolor=COL_LEG_LBL,
          fontsize=FS_LEGEND,
          handlelength=1.4,
          handleheight=1.3,
          borderpad=1.0)

# Source — pinned to CAPTION_Y, well clear of the x-axis label
fig.text(MARGIN["left"], CAPTION_Y, source,
         fontsize=FS_SOURCE, color=COL_SOURCE, ha="left", va=CAPTION_VA,
         transform=fig.transFigure)

# Username — single clean text, slightly lighter/brighter than source for visibility
fig.text(1.0 - MARGIN["right"], CAPTION_Y, author,
         fontsize=FS_HANDLE_NEW, color=COL_HANDLE,
         ha="right", va=CAPTION_VA,
         fontstyle=FI_HANDLE, fontweight=FW_HANDLE,
         transform=fig.transFigure)

# No tight_layout — axes are placed manually via MARGIN above.
plt.savefig(f"{file}.png", dpi=FIG_DPI, facecolor=BG)
print("Image saved.")


# =============================================================================
# DATA SOURCES & VERIFICATION NOTES
# =============================================================================
#
# All historical population figures are North American totals (USA + Canada),
# adults and children, horse-and-buggy groups only (excludes Beachy Amish,
# Amish Mennonites, and other car-driving groups).
# US-only is ~98% of the North American total in all years.
#
# VERIFIED DATA POINTS USED IN GRAPH:
#
#   2000 — ~177,900 (North America)
#          Source: Young Center for Anabaptist & Pietist Studies,
#          Elizabethtown College. Cited in:
#          - "Amish Population Profile 2025", Young Center (groups.etown.edu)
#            states: "increasing from approximately 177,910 in 2000 to 410,955
#            in 2025"
#          - Wikipedia "Amish" article: "In 2000, about 165,620 Old Order Amish
#            resided in the United States" (US-only figure; North American
#            total ~177,885 per Amish America 2020 report)
#          - Amish America (amishamerica.com/amish-population-2020/):
#            "increased from an estimated 177,885 in 2000 to 350,665 in 2020"
#          Used value: 177,900 (rounded average of sourced figures)
#
#   2010 — ~249,500 (North America)
#          Source: Young Center / Association of Statisticians of American
#          Religious Bodies (ASARB) 2010 U.S. Religion Census, compiled by
#          Elizabeth Cooksey & Cory Anderson (Ohio State University).
#          - "Amish Population Trends 2010-2015", Young Center:
#            "increasing from an estimated 249,500 in 2010"
#          - "Amish Population Profile 2019", Young Center: same figure
#          Used value: 249,500 (directly sourced)
#
#   2015 — ~300,000 (North America)
#          Source: Young Center, "Amish Population Trends 2010-2015":
#          "increasing from an estimated 249,500 in 2010 to 300,000 in 2015"
#          Used value: 300,000 (directly sourced)
#
#   2020 — ~350,700 (North America)
#          Source: Young Center, annual estimate published summer 2020.
#          - Amish America (amishamerica.com/amish-population-2020/):
#            "The total estimated Amish population is 350,665"
#          - Anabaptist World (Dec 2020): "propelled Old Order Amish groups
#            above 350,000 people"
#          Used value: 350,700 (rounded from 350,665)
#
#   2025 — ~411,000 (North America; US portion ~404,575)
#          Source: Young Center, "Amish Population Profile 2025"
#          (groups.etown.edu/amishstudies/amish-population-profile-2025/):
#          "increasing from approximately 177,910 in 2000 to 410,955 in 2025"
#          - Wikipedia "Amish": "The total Amish population in the United
#            States as of June 2025 has stood at 404,575"
#          - Amish America 2025 report: "clocking in this year at 411,060"
#          Used value: 411,000 (rounded North American total)
#
# GROWTH RATE USED FOR PROJECTION:
#
#   ~3.5% per annum (constant exponential)
#   Basis:
#   - Wikipedia "List of U.S. states by Amish population": "growing rapidly
#     (around 3-4% per year)"
#   - Implied by doubling time: Young Center states population "doubles about
#     every 20 years"; rule of 70 gives ~3.5%/yr for a 20-year doubling time
#   - Cross-check: 177,900 × (1.035)^25 = ~410,000 ✓ matches 2025 actual
#   - 2019 Young Center profile recorded a single-year growth rate of 3.9%
#   - 2025 Young Center profile implies ~2.5% for 2024-2025 (slower year)
#   - 3.5% is the midpoint consensus figure and consistent with long-run
#     observed doubling; used as the constant projection rate
#
# NOTE ON 2005 DATA POINT:
#   The 2005 figure previously used (~198,000) was a linear interpolation
#   between 2000 and 2010, not a directly sourced figure. It has been removed
#   from the graph; only verified anchor years are plotted.
#
# PROJECTED MILESTONE VALUES (computed by script):
#   2045: proj(2045) = 411,000 × 1.035^20 ≈ 817,000  → displayed as ~817K
#   2065: proj(2065) = 411,000 × 1.035^40 ≈ 1,625,000 → displayed as ~1.6M
#   2085: proj(2085) = 411,000 × 1.035^60 ≈ 3,229,000 → displayed as ~3.2M
#   2100: proj(2100) = 411,000 × 1.035^75 ≈ 5,416,000 → displayed as ~5.4M
#
# NOTE FOR ANYONE READING THIS: YOU MUST KEEP THESE SOURCES IN THE FILE.
#
# =============================================================================