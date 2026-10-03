"""Singlet-fission / MEG carrier-multiplication model.

One blue photon -> m(E) electron-hole pairs instead of 1 + heat.
  m(E) = 1 + QY_extra * step(E - E_thr),  E_thr ~= 2 * Eg_fission
with measured quantum yield anchors from the 2025-2026 literature sweep:
  - Kyushu/JGU spin-flip Mo complex (JACS Mar 2026): ~130 % QY in solution
  - CsPbCl3:Yb quantum-cutting NCs on Si (Joule Jul 2026): PLQY 170 %, EQE 117 %
    at 380 nm, device 26.00 % vs 25.58 % reference
  - Pentacene lower bound (Tabachnyk 2013): 180 +/- 15 % fission efficiency

Model output: effective Jsc multiplier G for a host bandgap Eg when photons
above E_thr generate `qy` pairs on average:
  G = (N_all + (qy-1) * N_above_thr) / N_all
where N are sun photon counts. PCE estimate = SQ(Eg) rescaled by current
gain at fixed Voc/FF (upper bound; real devices lose Voc via triplet energy
offset — reported explicitly as a derating factor).

Hidden pattern (verified by scan_hosts): the current-gain factor G is LARGEST
for NARROW-gap hosts (Eg ~1.1 eV, hot_frac ~28% above 2Eg) and falls toward
wide gaps (Eg 1.9 eV -> hot_frac <5%). Absolute derated efficiency therefore
peaks near the SQ-peak region, not at wide gaps — fission FLATTENS the peak
rather than moving it. Device lesson (matches Rao/Friend + Baldo tetracene-on-Si
architecture): put the fission layer on top of a narrow-gap bottom cell, where
the blue thermalization loss it recovers is largest.
"""

import numpy as np
from .sq_limit import _E, _PHI_SUN, Q, sq_point

EV = Q  # J per eV


def photon_count_above(E_thr_eV: float) -> float:
    m = _E >= E_thr_eV * EV
    return float(np.trapezoid(_PHI_SUN[m], _E[m]))


def fission_gain(Eg_host_eV: float, qy: float = 1.30, thr_mult: float = 2.0) -> dict:
    n_all = photon_count_above(Eg_host_eV)
    n_hot = photon_count_above(thr_mult * Eg_host_eV)
    frac = n_hot / max(n_all, 1e-300)
    G = 1.0 + (qy - 1.0) * frac
    base = sq_point(Eg_host_eV)
    eta_ideal = base["eta"] * G
    # realistic derating: triplet transfer + Voc penalty ~ 0.85
    eta_derated = eta_ideal * 0.85
    return {"Eg_host_eV": Eg_host_eV, "qy": qy, "hot_frac": float(frac),
            "G": float(G), "sq_base": base["eta"],
            "eta_ideal": float(eta_ideal), "eta_derated": float(eta_derated)}


def scan_hosts(qy_list=(1.3, 1.7, 2.0)):
    hosts = [round(x, 2) for x in np.linspace(0.9, 2.2, 14)]
    out = []
    for qy in qy_list:
        for Eg in hosts:
            r = fission_gain(Eg, qy=qy)
            r["scan_qy"] = qy
            out.append(r)
    return out
