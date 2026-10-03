"""Full benchmark harness: runs every model, checks physical ordering laws,
compares against certified records, writes machine-readable results + figures.

Run:  python -m src.benchmarks
Out:  results/benchmark.json, figures/*.png
Exit code != 0 if ANY verification law fails (CI-grade).
"""

import json
import os
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .sq_limit import sq_curve
from .tandem import scan_2j, scan_3j, tandem_point
from .rectenna import spectrum_weighted_eta, road_to_90_table
from .singlet_fission import fission_gain, scan_hosts
from .tpv import tpv_point, scan_temperature, near_field_boost, landsberg_limit
from .hot_carrier import hot_carrier_eta, cooling_ladder
from .records import RECORDS, SQ_1J_PEAK, LANDSBERG

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(HERE, "results")
FIG = os.path.join(HERE, "figures")


def check(cond, msg):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {msg}")
    return bool(cond)


def main():
    os.makedirs(RES, exist_ok=True)
    os.makedirs(FIG, exist_ok=True)
    ok = True
    out = {"records": RECORDS}

    # 1 — SQ curve ---------------------------------------------------------
    sq = sq_curve()
    out["sq_peak"] = sq["peak"]
    eg = np.array([r["Eg_eV"] for r in sq["rows"]])
    et = np.array([r["eta"] for r in sq["rows"]])
    ok &= check(1.15 <= sq["peak"]["Eg_eV"] <= 1.40,
                f"SQ peak gap {sq['peak']['Eg_eV']:.2f} eV in [1.15,1.40] (blackbody sun)")
    ok &= check(0.28 <= sq["peak"]["eta"] <= 0.33,
                f"SQ peak {sq['peak']['eta']*100:.2f}% in [28,33]% (blackbody sun; AM1.5G canon 33.7%)")
    si_pts = [r for r in sq["rows"] if abs(r["Eg_eV"] - 1.12) < 0.03]
    ok &= check(si_pts and si_pts[0]["eta"] > 0.281,
                f"SQ@Si(1.12eV)={si_pts[0]['eta']*100:.1f}% above certified 28.1% (no violation)")
    plt.figure()
    plt.plot(eg, et * 100)
    plt.axhline(28.1, ls="--", label="Si record 28.1% (2026)")
    plt.axhline(33.7, ls=":", label="SQ canonical 33.7%")
    plt.xlabel("Bandgap (eV)"); plt.ylabel("1-sun limit (%)")
    plt.title("Shockley-Queisser detailed balance (reproduced)")
    plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(FIG, "01_sq_curve.png"), dpi=130)

    # 2 — Tandems ----------------------------------------------------------
    b2 = scan_2j(); b3 = scan_3j()
    out["tandem_2j_best"] = b2; out["tandem_3j_best"] = b3
    ok &= check(0.42 <= b2["eta"] <= 0.48, f"2J bound {b2['eta']*100:.1f}% in [42,48]%")
    ok &= check(0.46 <= b3["eta"] <= 0.54, f"3J bound {b3['eta']*100:.1f}% in [46,54]%")
    ok &= check(b2["eta"] > sq["peak"]["eta"], "2J bound strictly above 1J peak")
    ok &= check(b3["eta"] > b2["eta"], "3J bound strictly above 2J bound")
    ok &= check(all(r["eta"] < b2["eta"] for r in RECORDS if r.get("kind") == "2J"),
                "all certified 2J records (<=35.5%) below 2J bound — headroom, no violation")
    ok &= check(all(r["eta"] < 0.90 for r in RECORDS if r.get("eta")),
                "no far-field junction record anywhere near 90% (junctions alone insufficient)")

    # 3 — Rectenna cliff ---------------------------------------------------
    eta_mim, fc_mim = spectrum_weighted_eta(100, 1.0)
    eta_goal, fc_goal = spectrum_weighted_eta(5, 0.05)
    out["rectenna"] = {"mim_100ohm_1fF": {"eta": eta_mim, "fc_THz": fc_mim},
                       "target_5ohm_0.05fF": {"eta": eta_goal, "fc_THz": fc_goal},
                       "roadmap": road_to_90_table()}
    ok &= check(fc_mim < 50, f"state-of-art MIM fc={fc_mim:.1f} THz << solar 200-1000 THz (explains <1% demos)")
    ok &= check(eta_mim < 0.05, f"MIM spectrum eta={eta_mim*100:.2f}% (<5%) consistent with literature")
    ok &= check(fc_goal > 300, f"target diode fc={fc_goal:.0f} THz reaches optical regime")
    ok &= check(eta_goal > 10 * eta_mim, "10x RC reduction buys >10x system eta (the cliff)")

    # 4 — Fission ----------------------------------------------------------
    f110 = fission_gain(1.1, qy=1.30)
    f130 = fission_gain(1.7, qy=1.30)
    f170 = fission_gain(1.7, qy=1.70)
    hosts = scan_hosts()
    best_der = max(hosts, key=lambda r: r["eta_derated"])
    out["fission"] = {"qy130_Eg1.1": f110, "qy130_Eg1.7": f130,
                      "qy170_Eg1.7": f170, "best_derated": best_der}
    ok &= check(f130["G"] > 1.0, f"QY130 gives current gain G={f130['G']:.3f} > 1")
    ok &= check(f170["G"] > f130["G"], "higher QY -> higher gain (monotone)")
    ok &= check(f110["G"] > fission_gain(1.9, qy=1.30)["G"],
                f"gain factor peaks at NARROW gaps G(1.1)={f110['G']:.3f} (tetracene-on-Si architecture)")
    ok &= check(f110["eta_ideal"] > f110["sq_base"],
                "ideal fission-augmented Si beats bare SQ at same gap (breaks 1J ceiling pre-derate)")
    ok &= check(best_der["Eg_host_eV"] <= 1.4,
                f"best derated host Eg={best_der['Eg_host_eV']}eV sits at/near SQ peak (fission flattens, not shifts)")
    ok &= check(best_der["eta_derated"] < LANDSBERG, "fission-boosted PCE stays under Landsberg (thermodynamics safe)")

    # 5 — TPV --------------------------------------------------------------
    bb = tpv_point(0.72, 1500, delta=10.0, suppr=1.0)
    scan = scan_temperature()
    sel = next(r for r in scan if r["Te_K"] == 1500)  # co-designed band
    nf10 = near_field_boost(10); nf1000 = near_field_boost(1000)
    out["tpv"] = {"blackbody_1500K": bb, "selective_1500K": sel,
                  "temp_scan_selective": scan,
                  "nearfield_10nm": nf10, "nearfield_1um": nf1000,
                  "landsberg": landsberg_limit()}
    ok &= check(all(r["eta"] > tpv_point(r["Eg_eV"], r["Te_K"], delta=10.0, suppr=1.0)["eta"]
                    for r in scan),
                "co-designed selective beats blackbody at EVERY emitter T (1000-2200 K)")
    ok &= check(sel["eta"] / bb["eta"] > 3.0,
                f"selective {sel['eta']*100:.1f}% >3x blackbody {bb['eta']*100:.1f}% @1500K")
    ok &= check(nf10 > 100 and nf1000 < 6, f"near-field 10nm x{nf10:.0f} >> 1um x{nf1000:.2f} (tunneling law)")
    ok &= check(abs(landsberg_limit() - 0.933) < 1e-9, "Landsberg 93.3% = only far-field number above 90%")

    # 6 — Hot carrier ------------------------------------------------------
    gaas = hot_carrier_eta(1.4, tau_cool_ps=0.5)
    pero = hot_carrier_eta(1.4, tau_cool_ps=150.0)
    lad = cooling_ladder()
    out["hot_carrier"] = {"gaAs_0.5ps": gaas, "perovskite_150ps": pero, "ladder": lad}
    ok &= check(pero["harvest_frac"] > 0.9 > gaas["harvest_frac"],
                f"150ps harvests {pero['harvest_frac']*100:.0f}% vs 0.5ps {gaas['harvest_frac']*100:.1f}% (window opens)")
    ok &= check(all(b["eta_hot"] >= a["eta_hot"] - 1e-12 for a, b in zip(lad, lad[1:])),
                "hot-carrier eta monotone in cooling time")
    ok &= check(pero["eta_hot"] < 0.90, "hot-carrier alone stays below 90% (needs stacking)")

    # 7 — Synthesis: the 90%+ map ------------------------------------------
    out["synthesis_90plus"] = {
        "junctions_alone_max_1sun": round(max(sq["peak"]["eta"], b2["eta"], b3["eta"]), 4),
        "junctions_can_reach_90": False,
        "credible_90plus_routes": [
            "TPV selective emitter + photon recycling -> Landsberg 93.3% (far-field legal)",
            "Near-field TPV (d<100nm): 100-500x power, quasi-monochromatic transfer",
            "Rectenna IF diode RC<0.3fs (fc>500THz): wave capture without thermalization",
            "Fission/MEG QY 130-200% stacked on wide-gap host + TPV/hot-carrier extraction",
        ],
    }
    ok &= check(out["synthesis_90plus"]["junctions_alone_max_1sun"] < 0.90,
                "junctions-alone maximum stays below 90% at 1-sun (core thesis)")

    with open(os.path.join(RES, "benchmark.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nWrote results/benchmark.json")
    print("RESULT:", "ALL CHECKS PASSED" if ok else "FAILURES PRESENT")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
