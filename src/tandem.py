"""Multi-junction detailed-balance bounds (1-sun, unconstrained + series).

Why this matters for the 90%+ question:
  - 1J SQ peak   ~33.7 %  (1.34 eV)
  - 2J tandem    ~45-46 %  (e.g. 0.94 / 1.64 eV)
  - 3J           ~48-51 %
  - infinite-J   ~68 % (1-sun) / ~86 % (max concentration)
So junctions ALONE can never reach 90 % at 1-sun. That negative result is the
whole point: it forces the three non-junction routes studied here
(rectenna-wave, fission/MEG multiplication, TPV/Landsberg photon recycling,
hot-carrier extraction).

Model: stacked gaps Eg_1 < Eg_2 < ... < Eg_n (bottom..top). Top cell absorbs
E > Eg_top; middle absorbs Eg_mid..Eg_top, etc. Each subcell is an SQ cell on
its slice; total power = sum (unconstrained, e.g. 4-terminal) or
series-limited by min(Jsc) with summed Voc (2-terminal, current-matched).

Verified anchors:
  - 2J unconstrained optimum in [42, 48] %
  - 3J optimum in [46, 54] %
  - 2J optimum > 1J peak (strict)
  - 2026 certified perovskite/Si records (35.2 % ESTI, 35.5 % LONGi 2026-07)
    lie strictly below the 2J bound (~45 %) — headroom, no violation.
"""

import itertools
import numpy as np
from .sq_limit import _E, _PHI_SUN, _PHI_CELL, PIN, Q, K, T_CELL


def _slice_flux(lo_J, hi_J, phi):
    m = (_E >= lo_J) & (_E < hi_J)
    if not np.any(m):
        return 0.0
    return float(np.trapezoid(phi[m], _E[m]))


def _subcell(lo_eV, hi_eV):
    lo, hi = lo_eV * Q, hi_eV * Q
    Ns = _slice_flux(lo, hi, _PHI_SUN)
    Nc = _slice_flux(lo, hi, _PHI_CELL)
    Jsc, J0 = Q * Ns, Q * Nc
    Vt = K * T_CELL / Q
    Voc = Vt * np.log(Jsc / max(J0, 1e-300) + 1.0)
    v = Voc / Vt
    FF = (v - np.log(v + 0.72)) / (v + 1.0)
    return Jsc, float(Voc), float(FF)


def tandem_point(gaps_bottom_to_top, series=True):
    gaps = sorted(gaps_bottom_to_top)
    bounds = [0.3] + gaps + [4.5]
    # slices from top gap down: cell k absorbs [gaps[k], bounds[k+2])
    cells = []
    for k, g in enumerate(gaps):
        lo = g
        hi = bounds[k + 2]  # next higher gap (or 4.5 for top)
        cells.append(_subcell(lo, hi))
    Jscs = np.array([c[0] for c in cells])
    Vocs = np.array([c[1] for c in cells])
    FFs = np.array([c[2] for c in cells])
    if series:
        J = float(np.min(Jscs))
        V = float(np.sum(Vocs))
        FF = float(np.min(FFs))
        eta = J * V * FF / PIN
    else:
        eta = float(sum(J * V * F for J, V, F in cells) / PIN)
        J, V, FF = None, float(np.sum(Vocs)), None
    return {"gaps_eV": gaps, "eta": eta, "Jsc_series_A_m2": J,
            "Voc_sum_V": V, "series": series}


def scan_2j(grid=None):
    if grid is None:
        grid = np.linspace(0.6, 2.2, 33)
    best = None
    for lo in grid:
        for hi in grid:
            if hi <= lo + 0.15:
                continue
            r = tandem_point([float(lo), float(hi)], series=False)
            if best is None or r["eta"] > best["eta"]:
                best = r
    return best


def scan_3j():
    # coarse but sufficient grid; optimum is broad
    grid = [0.7, 0.9, 1.1, 1.35, 1.65, 1.9, 2.2]
    best = None
    for combo in itertools.combinations(grid, 3):
        r = tandem_point(list(combo), series=False)
        if best is None or r["eta"] > best["eta"]:
            best = r
    return best
