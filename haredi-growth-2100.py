import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patheffects import withStroke

# =============================================================================
# PROJECT SETUP
# =============================================================================
file   = "images/haredi_population_2100"
author = "@MarinoLinic"
source = "Sources: Pew Research Center, JPR, Prof. Joshua Comenetz"
title  = "Ultra-Orthodox (Haredi) Jewish Population in the USA"

# =============================================================================
# THEME SELECTOR
# =============================================================================
# Choose one of: "dark" | "light" | "amber" | "midnight" | "nordic" | "neon"
THEME = "light"

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
        COL_HANDLE    = "#c8e8f8",
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
        COL_HANDLE    = "#4a3080",
        COL_LEG_LBL   = "#404030",
        COL_LEG_EDGE  = "#c0b8a8",
        COL_GLOW      = "#f4f1eb",
    ),
    # ── Amber (warm dark) ────────────────────────────────────────────────────
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
        COL_HANDLE    = "#f0c878",
        COL_LEG_LBL   = "#c0a070",
        COL_LEG_EDGE  = "#403020",
        COL_GLOW      = "#110d08",
    ),
    # ── Midnight Blue ────────────────────────────────────────────────────────
    "midnight": dict(
        BG            = "#03060f",
        BG_AX         = "#050a18",
        COL_HIST      = "#00aaff",
        COL_MARK      = "#00aaff",
        COL_PROJ_A    = "#00ff88",
        COL_PROJ_B    = "#00ccff",
        COL_FILL_H    = "#00aaff",
        COL_GRID_Y    = "#0a1428",
        COL_GRID_X    = "#080f20",
        COL_SPINE     = "#102040",
        COL_TICK      = "#2050a0",
        COL_TITLE     = "#d0eeff",
        COL_AXIS_LBL  = "#2050a0",
        COL_ANNOT_TXT = "#d0eeff",
        COL_ANNOT_BG  = "#020510",
        COL_ANNOT_EC  = "#103060",
        COL_ANNOT_AR  = "#103060",
        COL_SOURCE    = "#204880",
        COL_HANDLE    = "#00ff88",
        COL_LEG_LBL   = "#80c8ff",
        COL_LEG_EDGE  = "#102848",
        COL_GLOW      = "#03060f",
    ),
    # ── Nordic ───────────────────────────────────────────────────────────────
    "nordic": dict(
        BG            = "#e8eef4",
        BG_AX         = "#f4f8fc",
        COL_HIST      = "#bf616a",
        COL_MARK      = "#bf616a",
        COL_PROJ_A    = "#5e81ac",
        COL_PROJ_B    = "#b48ead",
        COL_FILL_H    = "#bf616a",
        COL_GRID_Y    = "#d0dae4",
        COL_GRID_X    = "#dce4ec",
        COL_SPINE     = "#b8c8d8",
        COL_TICK      = "#607888",
        COL_TITLE     = "#2e3440",
        COL_AXIS_LBL  = "#607888",
        COL_ANNOT_TXT = "#2e3440",
        COL_ANNOT_BG  = "#ecf0f4",
        COL_ANNOT_EC  = "#a8b8c8",
        COL_ANNOT_AR  = "#90a8b8",
        COL_SOURCE    = "#7888a0",
        COL_HANDLE    = "#5e81ac",
        COL_LEG_LBL   = "#3b4252",
        COL_LEG_EDGE  = "#b0c0d0",
        COL_GLOW      = "#e8eef4",
    ),
    # ── Neon Tokyo ───────────────────────────────────────────────────────────
    "neon": dict(
        BG            = "#08060e",
        BG_AX         = "#0d0a16",
        COL_HIST      = "#ff2d78",
        COL_MARK      = "#ff2d78",
        COL_PROJ_A    = "#39ff14",
        COL_PROJ_B    = "#bf00ff",
        COL_FILL_H    = "#ff2d78",
        COL_GRID_Y    = "#150f22",
        COL_GRID_X    = "#100c1a",
        COL_SPINE     = "#2a1a40",
        COL_TICK      = "#5a3a80",
        COL_TITLE     = "#f0e0ff",
        COL_AXIS_LBL  = "#5a3a80",
        COL_ANNOT_TXT = "#f0e0ff",
        COL_ANNOT_BG  = "#060410",
        COL_ANNOT_EC  = "#3a1a58",
        COL_ANNOT_AR  = "#3a1a58",
        COL_SOURCE    = "#4a2870",
        COL_HANDLE    = "#ff2d78",
        COL_LEG_LBL   = "#c080ff",
        COL_LEG_EDGE  = "#2a1a40",
        COL_GLOW      = "#08060e",
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
FS_HANDLE     = 17

FW_TITLE      = "bold"
FW_ANNOT      = "bold"
FW_HANDLE     = "bold"

FF_TITLE      = "serif"
FS_TITLE_PAD  = 20
FI_HANDLE     = "italic"

# =============================================================================
# FIGURE & EXPORT
# =============================================================================
FIG_W         = 14
FIG_H         = 9.6
FIG_DPI       = 400

MARGIN = dict(
    top    = 0.12,
    bottom = 0.16,
    left   = 0.09,
    right  = 0.04,
)

CAPTION_Y        = 0.032
CAPTION_VA       = "bottom"

FS_HANDLE_NEW    = 20
HANDLE_GLOW_LW   = 4

# Scaled up relative to original because max pop hits ~11M instead of ~5.4M
FIXED_OFFSET  = 850_000

# =============================================================================
# DATA
# =============================================================================
years      = np.arange(2000, 2101, 1)
base_year  = 2020
base_pop   = 700_000
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

historical = {
    2000: 360_000,
    2006: 468_000,
    2013: 530_000,
    2020: 700_000,
}
hist_years = np.array(list(historical.keys()))
hist_pops  = np.array(list(historical.values()))

milestone_years =[2020, 2040, 2060, 2080, 2100]
milestones: dict[int, tuple[int, str]] = {}
for yr in milestone_years:
    p = historical.get(yr, proj(yr))
    label = "700K  (2020)" if yr == 2020 else fmt_pop(proj(yr))
    milestones[yr] = (p, label)

# =============================================================================
# FIGURE
# =============================================================================
fig = plt.figure(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor(BG)

ax = fig.add_axes((
    MARGIN["left"],
    MARGIN["bottom"],
    1.0 - MARGIN["left"] - MARGIN["right"],
    1.0 - MARGIN["top"]  - MARGIN["bottom"],
))
ax.set_facecolor(BG_AX)

# Gradient projected line
proj_mask = years >= 2020
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
    t = max(0.0, (yr - 2020) / (2100 - 2020))
    dot_color = COL_HIST if yr <= 2020 else cmap_proj(t)
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

# Base Year marker
ax.axvline(x=2020, color=COL_MARK, linewidth=0.8,
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

# Title
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
                             label=f"Projected  ·  2020–2100  ·  ~{growth_rate*100:.1f}%/yr")
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

# Source
fig.text(MARGIN["left"], CAPTION_Y, source,
         fontsize=FS_SOURCE, color=COL_SOURCE, ha="left", va=CAPTION_VA,
         transform=fig.transFigure)

# Username
fig.text(1.0 - MARGIN["right"], CAPTION_Y, author,
         fontsize=FS_HANDLE_NEW, color=COL_HANDLE,
         ha="right", va=CAPTION_VA,
         fontstyle=FI_HANDLE, fontweight=FW_HANDLE,
         transform=fig.transFigure)

plt.savefig(f"{file}-{THEME}.png", dpi=FIG_DPI, facecolor=BG)
print("Image saved.")

# =============================================================================
# DATA SOURCES & VERIFICATION NOTES
# =============================================================================
#
# VERIFIED DATA POINTS USED IN GRAPH:
#
#   2000 — ~360,000
#          Source: Estimate by demographer Prof. Joshua Comenetz (University
#          of Florida), widely cited in demographic literature and Wikipedia.
#          Used value: 360,000
#
#   2006 — ~468,000
#          Source: Follow-up estimate by Comenetz showing a 30% increase
#          over the 2000 baseline.
#          Used value: 468,000
#
#   2013 — ~530,000
#          Source: Pew Research Center, "A Portrait of Jewish Americans" (2013).
#          Estimated that roughly 10% of the American Jewish population
#          (5.3 million) identified as ultra-Orthodox.
#          Used value: 530,000
#
#   2020 — ~700,000
#          Source: Pew Research Center, "Jewish Americans in 2020" survey,
#          and the Institute for Jewish Policy Research (JPR) 2020 report
#          "The global haredi population."
#          Used value: 700,000
#
# GROWTH RATE USED FOR PROJECTION:
#
#   ~3.5% per annum (constant exponential)
#   Basis:
#   - JPR (Institute for Jewish Policy Research) 2020 report: "the Haredi
#     population grew at about 3.5%-4.0% annually."
#   - Widely recognized doubling time of roughly 20 years.
#
# PROJECTED MILESTONE VALUES (computed by script):
#   2040: proj(2040) = 700,000 × 1.035^20 ≈ 1,392,000  → displayed as ~1.4M
#   2060: proj(2060) = 700,000 × 1.035^40 ≈ 2,771,000  → displayed as ~2.8M
#   2080: proj(2080) = 700,000 × 1.035^60 ≈ 5,514,000  → displayed as ~5.5M
#   2100: proj(2100) = 700,000 × 1.035^80 ≈ 10,973,000 → displayed as ~11M
#
# NOTE FOR ANYONE READING THIS: YOU MUST KEEP THESE SOURCES IN THE FILE.
#
# =============================================================================