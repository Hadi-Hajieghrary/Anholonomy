"""Shared IEEE-journal figure style for every generated plot in this repo.

IEEE guidance applied (per the Author Center graphics rules):
  * vector PDF for line art; fonts embedded (Type-42 TrueType) so the PDF
    carries no font dependency;
  * a Times-metric serif (STIXGeneral) for text and STIX for math, matching
    IEEE body type; consistent sizes across every figure;
  * ~8 pt text at final (column) size, so nothing shrinks below ~7 pt after
    reduction; single-column width 3.5 in, double-column 7.16 in;
  * 400 dpi for any raster element (>300 dpi requirement);
  * colour is never the sole cue -- helpers below hand out distinct
    (colour, linestyle, marker) triples so the figure survives grayscale.

Usage in a generator:
    from analysis.ieee_style import apply_ieee, COLW, DBLW, cyc
    apply_ieee()
    fig, ax = plt.subplots(figsize=(COLW, COLW*0.75))   # ONE axes per figure
    sty = cyc()
    ax.plot(x, y, **next(sty), label=...)
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

COLW = 3.5          # IEEE single-column width (in)
DBLW = 7.16         # IEEE double-column width (in)

# colour-blind-safe Okabe-Ito ordering, each paired with a linestyle + marker
_PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00",
            "#56B4E9", "#000000", "#F0E442"]
_LS = ["-", "--", "-.", ":", "-", "--", "-.", ":"]
_MK = ["o", "s", "^", "D", "v", "P", "X", "*"]


def apply_ieee():
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 8,
        "axes.titlesize": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "figure.titlesize": 8,
        "axes.linewidth": 0.6,
        "lines.linewidth": 1.2,
        "lines.markersize": 3.5,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "legend.frameon": True,
        "legend.framealpha": 0.9,
        "legend.handlelength": 2.2,
        "legend.borderpad": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 150,
        "savefig.dpi": 400,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def cyc():
    """Yield {'color','linestyle','marker'} triples so series stay distinct
    without relying on colour."""
    i = 0
    while True:
        k = i % len(_PALETTE)
        yield {"color": _PALETTE[k], "linestyle": _LS[k], "marker": _MK[k]}
        i += 1


def color(i):
    return _PALETTE[i % len(_PALETTE)]


def save(fig, path):
    """Save vector PDF + a 400-dpi PNG twin (same basename)."""
    fig.savefig(path + ".pdf")
    fig.savefig(path + ".png", dpi=400)
    plt.close(fig)
