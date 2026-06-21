import json, math
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.transforms as mtransforms
from matplotlib.patches import PathPatch, FancyBboxPatch
from matplotlib.path import Path

REGIONS = {
    "Dalmatia": {
        "ids": {"HR.ZD", "HR.SB", "HR.SD", "HR.DN"},
        "pop_pct": 20.6, "player_pct": 47.4, "players": 9, "factor": 2.30,
    },
    "Zagreb &\nCentral": {
        "ids": {"HR.GZ", "HR.ZG", "HR.SM", "HR.KA"},
        "pop_pct": 27.5, "player_pct": 31.6, "players": 6, "factor": 1.15,
    },
    "Slavonia": {
        "ids": {"HR.OB", "HR.VS", "HR.SP", "HR.PS", "HR.BB", "HR.VP"},
        "pop_pct": 17.3, "player_pct": 10.5, "players": 2, "factor": 0.61,
    },
    "Western\nCroatia": {
        "ids": {"HR.IS", "HR.PG", "HR.LS"},
        "pop_pct": 13.0, "player_pct": 5.3, "players": 1, "factor": 0.41,
    },
    "Northern\n& Inland": {
        "ids": {"HR.KZ", "HR.VA", "HR.ME", "HR.KK"},
        "pop_pct": 21.6, "player_pct": 5.3, "players": 1, "factor": 0.25,
    },
}

hasc_to_region = {}
for rname, rdata in REGIONS.items():
    for h in rdata["ids"]:
        hasc_to_region[h] = rname

# ---------------------------------------------------------------------------
# Modern palette -- a wine/magenta <-> teal duotone instead of the classic
# red/blue ColorBrewer scheme. Anchored to data, so chip colors below are
# literally pulled from the same scale (no separate palette to keep in sync).
# ---------------------------------------------------------------------------
PAGE_BG     = "#EAE3D8"   # outer page
CARD_BG     = "#FCFAF6"   # card the chart sits on
OCEAN       = "#E7EFEC"   # sea fill
INK         = "#1E2B29"   # near-black text
MUTED       = "#7A766D"   # source-line gray
ACCENT_WINE = "#7A2049"   # under-represented chip / scale extreme
ACCENT_TEAL = "#0B5C53"   # over-represented chip / scale extreme

VMIN_FACTOR = 0.25
VMAX_FACTOR = 3.00

cmap = mcolors.LinearSegmentedColormap.from_list(
    "overrep_modern",
    [
        (0.0,  ACCENT_WINE),
        (0.35, "#E6A6BE"),
        (0.5,  "#FBF6EF"),
        (0.65, "#8FD6C8"),
        (1.0,  ACCENT_TEAL),
    ]
)

norm = mcolors.TwoSlopeNorm(vmin=math.log(VMIN_FACTOR), vcenter=0.0, vmax=math.log(VMAX_FACTOR))

def factor_to_color(factor):
    return cmap(norm(math.log(max(factor, 1e-6))))

for rname, rdata in REGIONS.items():
    rdata["color"] = factor_to_color(rdata["factor"])

# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
with open("gadm41_HRV_1.json", encoding="utf-8") as f:
    geojson = json.load(f)

LAT_CENTER = 44.5
LON_SCALE = math.cos(math.radians(LAT_CENTER))

def tx(lon, lat):
    return lon * LON_SCALE, lat

def transform_geom(geom):
    return {"type": geom["type"],
            "coordinates": [[[tx(lo, la) for lo, la in ring]
                              for ring in poly]
                             for poly in geom["coordinates"]]}

def path_for_geom(geom):
    verts, codes = [], []
    for poly in geom["coordinates"]:
        for ring in poly:
            codes += [Path.MOVETO] + [Path.LINETO]*(len(ring)-2) + [Path.CLOSEPOLY]
            verts += ring
    return verts, codes

def make_patch(geom, color, edgecolor="white", lw=0.7):
    verts, codes = path_for_geom(geom)
    return PathPatch(Path(verts, codes), facecolor=color, edgecolor=edgecolor, linewidth=lw)

all_x, all_y = [], []
all_verts, all_codes = [], []
for feat in geojson["features"]:
    g = transform_geom(feat["geometry"])
    v, c = path_for_geom(g)
    all_verts += v
    all_codes += c
    for poly in feat["geometry"]["coordinates"]:
        for ring in poly:
            for lo, la in ring:
                px, py = tx(lo, la)
                all_x.append(px); all_y.append(py)

x_min, x_max = min(all_x), max(all_x)
y_min, y_max = min(all_y), max(all_y)
map_w = x_max - x_min
map_h = y_max - y_min
aspect = map_w / map_h

# ---------------------------------------------------------------------------
# Layout, computed in inches so the map's true aspect ratio is always
# honored exactly (see fix history -- this avoids the squish bug for good).
# ---------------------------------------------------------------------------
TITLE_H_IN        = 1.05
SOURCE_H_IN       = 0.58
LEFT_MARGIN_IN    = 0.30
MAP_H_IN          = 5.4
GAP_IN            = 0.55
CBAR_W_IN         = 0.36
CBAR_LABELS_W_IN  = 1.55
RIGHT_MARGIN_IN   = 0.30

MAP_W_IN = MAP_H_IN * aspect
FIG_W = LEFT_MARGIN_IN + MAP_W_IN + GAP_IN + CBAR_W_IN + CBAR_LABELS_W_IN + RIGHT_MARGIN_IN
FIG_H = TITLE_H_IN + MAP_H_IN + SOURCE_H_IN

fig = plt.figure(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor(PAGE_BG)

# --- rounded "card" the whole chart sits on ---
card_ax = fig.add_axes([0, 0, 1, 1], zorder=0)
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

ax_left   = LEFT_MARGIN_IN / FIG_W
ax_bottom = SOURCE_H_IN / FIG_H
ax_width  = MAP_W_IN / FIG_W
ax_height = MAP_H_IN / FIG_H
ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height], zorder=2)

cax_left   = (LEFT_MARGIN_IN + MAP_W_IN + GAP_IN) / FIG_W
cax_width  = CBAR_W_IN / FIG_W
cax_height = 0.62 * MAP_H_IN / FIG_H
cax_bottom = ax_bottom + 0.5 * (ax_height - cax_height)
cax = fig.add_axes([cax_left, cax_bottom, cax_width, cax_height], zorder=2)

ax.set_facecolor(OCEAN)

# soft drop shadow under the whole country silhouette, drawn once as a
# single offset shape behind the colored regions (cleaner than per-region
# shadows, which would seam at every internal border)
shadow_patch = PathPatch(Path(all_verts, all_codes), facecolor="#0B1F1C",
                          edgecolor="none", alpha=0.20, zorder=2.1)
shadow_patch.set_transform(
    mtransforms.offset_copy(ax.transData, fig=fig, x=1.6, y=-2.0, units="points")
)
ax.add_patch(shadow_patch)

for feat in geojson["features"]:
    hasc   = feat["properties"]["HASC_1"]
    region = hasc_to_region.get(hasc, "Unknown")
    color  = REGIONS.get(region, {}).get("color", "#ccc")
    g = transform_geom(feat["geometry"])
    ax.add_patch(make_patch(g, color=color, edgecolor=CARD_BG, lw=0.9))

pad_x = map_w * 0.05
pad_y = map_h * 0.04
ax.set_xlim(x_min - pad_x, x_max + pad_x)
ax.set_ylim(y_min - pad_y, y_max + pad_y)
ax.set_aspect("equal")
ax.axis("off")

# --- labels: plain shadowed name + a bold value chip ---
LABEL_POS = {
    "Dalmatia":           (16.85, 43.55),
    "Zagreb &\nCentral":  (16.00, 45.40),
    "Slavonia":           (17.90, 45.25),
    "Western\nCroatia":   (15.00, 45.25),
    "Northern\n& Inland": (16.50, 46.05),
}

NAME_DY   = map_h * 0.046
FACTOR_DY = map_h * 0.040

for rname, (lon, lat) in LABEL_POS.items():
    px, py = tx(lon, lat)
    rdata = REGIONS[rname]
    bg = rdata["color"]
    lum = 0.299*bg[0] + 0.587*bg[1] + 0.114*bg[2]
    if lum < 0.55:
        name_color, outline_col = "white", "#102422"
    else:
        name_color, outline_col = "#14201F", "#F4F1EA"
    t1 = ax.text(px, py + NAME_DY, rname, ha="center", va="center",
                 fontsize=10, fontweight="bold", color=name_color,
                 linespacing=1.3, zorder=5)
    t1.set_path_effects([pe.withStroke(linewidth=2.1, foreground=outline_col, alpha=0.95)])

    chip_color = ACCENT_TEAL if rdata["factor"] >= 1.0 else ACCENT_WINE
    t2 = ax.text(px, py - FACTOR_DY, f"{rdata['factor']:.2f}\u00d7",
                 ha="center", va="center", fontsize=14.5,
                 fontweight="bold", color="white", zorder=6,
                 bbox=dict(boxstyle="round,pad=0.38,rounding_size=0.4",
                           facecolor=chip_color, edgecolor="none", alpha=0.96))
    t2.get_bbox_patch().set_path_effects(
        [pe.withSimplePatchShadow(offset=(1.5, -1.8), alpha=0.30, shadow_rgbFace="#000000")]
    )

# --- colorbar ---
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cb = fig.colorbar(sm, cax=cax, extend="neither")
cb.outline.set_visible(False)
cb.set_label("Overrepresentation\n(player % \u00f7 pop %)", fontsize=9,
             labelpad=10, fontweight="medium", color=INK)

tick_factors = [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
cb.set_ticks([math.log(f) for f in tick_factors])
cb.set_ticklabels([f"{f:.2f}\u00d7" for f in tick_factors])
for lbl in cb.ax.get_yticklabels():
    lbl.set_fontsize(8.5)
    lbl.set_color(INK)
cb.ax.tick_params(length=0)
cax.axhline(y=0, color=INK, linewidth=1.1, linestyle=(0, (4, 3)), alpha=0.55)

# --- titles ---
ax.text(0.0, 1.135, "Regional Representation in Croatian Football",
         transform=ax.transAxes, ha="left", va="bottom",
         fontsize=17, fontweight="bold", color=INK)
ax.text(0.0, 1.045, "2018 FIFA World Cup Squad  \u00b7  Croatian-born players only (n = 19)",
         transform=ax.transAxes, ha="left", va="bottom",
         fontsize=10.5, fontweight="medium", color=ACCENT_TEAL)

fig.text(
    ax_left, SOURCE_H_IN / FIG_H * 0.72,
    "Source: Croatian Bureau of Statistics 2021 census & 2018 WC squad birthplace analysis",
    ha="left", va="center", fontsize=7, color=MUTED,
)
fig.text(
    ax_left, SOURCE_H_IN / FIG_H * 0.30,
    "Dalmatia = Zadar, \u0160ibenik-Knin, Split-Dalmatia & Dubrovnik-Neretva  \u00b7  4 foreign-born players excluded",
    ha="left", va="center", fontsize=7, color=MUTED,
)

# --- credit tag ---
fig.text(
    1 - RIGHT_MARGIN_IN/FIG_W*0.55, SOURCE_H_IN / FIG_H * 0.30,
    "@MarinoLinich",
    ha="right", va="center", fontsize=8.5, fontweight="bold", color=ACCENT_TEAL,
)

out = "croatia_football_map.png"
plt.savefig(out, dpi=400, bbox_inches="tight", pad_inches=0.22, facecolor=PAGE_BG)
print("Saved:", out)