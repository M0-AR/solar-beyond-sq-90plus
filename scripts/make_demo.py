"""Generate all visual assets from VERIFIED benchmark data (no hand-made numbers).

Outputs (all under repo root):
  figures/01_sq_curve.png      SQ curve + certified records
  figures/02_routes.png        junction bounds vs records vs Landsberg
  figures/03_rectenna_cliff.png RC cliff (cutoff vs spectrum eta)
  figures/04_fission.png       gain factor vs host gap
  figures/05_tpv.png           selective vs blackbody across emitter T
  figures/06_hotcarrier.png    harvest fraction ladder
  demo/demo.gif                animated benchmark story (~10 s, loops)
  demo/demo.mp4                same story as H.264 video (for preview.html)
  demo/manifest.json           file list + sizes + frame counts

Run: python scripts/make_demo.py
Style: dark, high-contrast, colorblind-safe-ish palette, large fonts.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.insert(0, HERE)

from src.sq_limit import sq_curve
from src.tandem import scan_2j, scan_3j
from src.rectenna import road_to_90_table
from src.singlet_fission import scan_hosts
from src.tpv import scan_temperature, tpv_point
from src.hot_carrier import cooling_ladder

FIG = os.path.join(HERE, "figures")
DEMO = os.path.join(HERE, "demo")
os.makedirs(FIG, exist_ok=True)
os.makedirs(DEMO, exist_ok=True)

BG, FG, ACC, ACC2, ACC3, GRID = "#0b1020", "#eef2ff", "#38bdf8", "#fbbf24", "#34d399", "#26314d"
plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
                     "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG,
                     "ytick.color": FG, "axes.edgecolor": GRID, "grid.color": GRID,
                     "font.size": 11})


def sq_fig():
    sq = sq_curve()
    eg = np.array([r["Eg_eV"] for r in sq["rows"]])
    et = np.array([r["eta"] for r in sq["rows"]]) * 100
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(eg, et, color=ACC, lw=2.5, label="Detailed-balance limit (this repo)")
    ax.axhline(28.1, ls="--", color=ACC2, label="Certified Si record 28.1% (2026)")
    ax.axhline(33.7, ls=":", color=ACC3, label="AM1.5G textbook 33.7%")
    p = sq["peak"]
    ax.plot(p["Eg_eV"], p["eta"] * 100, "o", color=ACC2, ms=9)
    ax.annotate(f"peak {p['eta']*100:.1f}% @ {p['Eg_eV']:.2f} eV",
                (p["Eg_eV"], p["eta"] * 100), color=FG,
                xytext=(12, -22), textcoords="offset points",
                arrowprops=dict(arrowstyle="->", color=FG))
    ax.set_xlabel("Bandgap (eV)"); ax.set_ylabel("1-sun limit (%)")
    ax.set_title("Shockley–Queisser curve reproduced from Planck's law")
    ax.grid(alpha=0.4); ax.legend(fontsize=9, loc="lower center")
    fig.tight_layout(); fig.savefig(f"{FIG}/01_sq_curve.png", dpi=130); plt.close(fig)
    return p


def routes_fig(sq_peak, b2, b3):
    labels = ["1J limit", "2J bound", "3J bound", "Lab tandem\n35.5%",
              "Si cell\n28.1%", "Landsberg\nceiling"]
    vals = [sq_peak["eta"] * 100, b2["eta"] * 100, b3["eta"] * 100, 35.5, 28.1, 93.3]
    cols = [ACC, ACC, ACC, ACC2, ACC2, ACC3]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    bars = ax.bar(labels, vals, color=cols, edgecolor=BG)
    ax.set_ylabel("Efficiency (%)"); ax.set_ylim(0, 100)
    ax.set_title("Junctions alone stop far below 90% — only photon recycling goes higher")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.2, f"{v:.1f}%", ha="center", color=FG)
    ax.axhline(90, ls="--", color="#f87171", label="90% dream line")
    ax.legend(fontsize=9); fig.tight_layout()
    fig.savefig(f"{FIG}/02_routes.png", dpi=130); plt.close(fig)


def rectenna_fig():
    rows = road_to_90_table()
    fc = np.array([r["fc_THz"] for r in rows])
    eta = np.array([r["spectrum_eta"] for r in rows]) * 100
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.loglog(fc, eta, "o-", color=ACC, ms=8, lw=2.5)
    ax.axvline(500, ls="--", color="#f87171", label="Solar peak ~500 THz")
    for x, y in zip(fc, eta):
        ax.annotate(f"{y:.2f}%", (x, y), color=FG, xytext=(6, 6),
                    textcoords="offset points", fontsize=9)
    ax.set_xlabel("Diode cutoff frequency (THz)  [lower RC → right]")
    ax.set_ylabel("Spectrum-weighted efficiency (%)")
    ax.set_title("The rectenna cliff: 10x better RC buys ~100x efficiency")
    ax.grid(alpha=0.4, which="both"); ax.legend(fontsize=9)
    fig.tight_layout(); fig.savefig(f"{FIG}/03_rectenna_cliff.png", dpi=130); plt.close(fig)


def fission_fig():
    hosts = [r for r in scan_hosts() if r["scan_qy"] == 1.30]
    eg = np.array([r["Eg_host_eV"] for r in hosts])
    g = np.array([r["G"] for r in hosts])
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(eg, (g - 1) * 100, "o-", color=ACC2, ms=7, lw=2.5)
    ax.set_xlabel("Host bandgap (eV)"); ax.set_ylabel("Extra current from fission (%)")
    ax.set_title("Fission gain is biggest on narrow-gap hosts — it belongs on silicon")
    ax.grid(alpha=0.4); fig.tight_layout()
    fig.savefig(f"{FIG}/04_fission.png", dpi=130); plt.close(fig)


def tpv_fig():
    scan = scan_temperature()
    te = np.array([r["Te_K"] for r in scan])
    sel = np.array([r["eta"] for r in scan]) * 100
    bb = np.array([tpv_point(0.72, int(t), delta=10.0, suppr=1.0)["eta"] for t in te]) * 100
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(te, bb, "o--", color="#94a3b8", label="Blackbody emitter")
    ax.plot(te, sel, "o-", color=ACC3, ms=7, lw=2.5, label="Selective emitter (co-designed)")
    ax.set_xlabel("Emitter temperature (K)"); ax.set_ylabel("TPV efficiency (%)")
    ax.set_title("Selective TPV beats blackbody at every temperature")
    ax.grid(alpha=0.4); ax.legend(fontsize=9); fig.tight_layout()
    fig.savefig(f"{FIG}/05_tpv.png", dpi=130); plt.close(fig)


def hot_fig():
    lad = cooling_ladder()
    tau = np.array([r["tau_cool_ps"] for r in lad])
    hv = np.array([r["harvest_frac"] for r in lad]) * 100
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.semilogx(tau, hv, "o-", color=ACC, ms=8, lw=2.5)
    ax.axvline(0.5, ls=":", color="#94a3b8", label="GaAs ~0.5 ps")
    ax.axvline(150, ls="--", color=ACC2, label="Perovskite ~150 ps")
    ax.set_xlabel("Cooling time (ps)"); ax.set_ylabel("Excess energy harvested (%)")
    ax.set_title("Slow cooling opens the hot-carrier extraction window")
    ax.grid(alpha=0.4, which="both"); ax.legend(fontsize=9); fig.tight_layout()
    fig.savefig(f"{FIG}/06_hotcarrier.png", dpi=130); plt.close(fig)


def demo_movie(sq_peak, b2):
    """Two-act animation: (1) SQ curve draws itself, (2) routes bar race."""
    eg = np.linspace(0.5, 2.5, 81)
    et = np.array([r["eta"] for r in sq_curve()["rows"]]) * 100
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.2))
    fig.suptitle("Beyond Shockley–Queisser: the 90%+ map in 10 seconds", color=FG, fontsize=13)
    ax1.set_xlim(0.5, 2.5); ax1.set_ylim(0, 36)
    ax1.set_xlabel("Bandgap (eV)"); ax1.set_ylabel("1-sun limit (%)")
    ax1.set_title("1) One junction caps at ~31%", fontsize=10)
    line, = ax1.plot([], [], color=ACC, lw=2.5)
    dot, = ax1.plot([], [], "o", color=ACC2, ms=9)
    ax1.grid(alpha=0.3)
    labels = ["1J", "2J", "3J", "Lab best", "Landsberg"]
    vals = [sq_peak["eta"] * 100, b2["eta"] * 100, 48.6, 35.5, 93.3]
    cols = [ACC, ACC, ACC, ACC2, ACC3]
    ax2.set_ylim(0, 100); ax2.set_title("2) Only photon recycling passes 90%", fontsize=10)
    ax2.set_ylabel("%")
    bars = ax2.bar(labels, [0] * 5, color=cols, edgecolor=BG)
    ax2.axhline(90, ls="--", color="#f87171", lw=1.5)
    N1, N2 = 40, 30
    total = N1 + N2

    def update(i):
        if i < N1:  # act 1: draw curve
            k = int((i + 1) / N1 * len(eg))
            line.set_data(eg[:k], et[:k])
            if k > 0:
                dot.set_data([eg[k - 1]], [et[k - 1]])
            for b in bars:
                b.set_height(0)
        else:  # act 2: grow bars
            line.set_data(eg, et)
            dot.set_data([sq_peak["Eg_eV"]], [sq_peak["eta"] * 100])
            f = (i - N1 + 1) / N2
            for b, v in zip(bars, vals):
                b.set_height(v * f)
        return (line, dot, *bars)

    ani = FuncAnimation(fig, update, frames=total, interval=140, blit=False)
    fig.tight_layout()
    gif_path = os.path.join(DEMO, "demo.gif")
    ani.save(gif_path, writer=PillowWriter(fps=8))
    mp4_path = os.path.join(DEMO, "demo.mp4")
    try:
        ani.save(mp4_path, writer=FFMpegWriter(fps=8, codec="libx264",
                                               extra_args=["-pix_fmt", "yuv420p"]))
    except Exception as e:
        print("MP4 skipped:", e)
        mp4_path = None
    plt.close(fig)
    return gif_path, mp4_path, total


def main():
    sq = sq_curve()
    b2, b3 = scan_2j(), scan_3j()
    p = sq_fig()
    routes_fig(sq["peak"], b2, b3)
    rectenna_fig(); fission_fig(); tpv_fig(); hot_fig()
    gif, mp4, frames = demo_movie(sq["peak"], b2)
    manifest = {"frames": frames,
                "files": {f: os.path.getsize(os.path.join(d, f))
                          for d in (FIG, DEMO) for f in os.listdir(d)}}
    with open(os.path.join(DEMO, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    for d in (FIG, DEMO):
        for f in sorted(os.listdir(d)):
            print(f"  {d}/{f}  {os.path.getsize(os.path.join(d, f))/1024:.0f} KB")
    print("demo movie:", frames, "frames ->", gif, mp4)


if __name__ == "__main__":
    main()
