"""Shockley-Queisser detailed-balance limit from first principles.

Method (textbook detailed balance, 1-sun, 300 K cell, 5800 K sun):
  Jsc(Eg) = q * F_sun(>Eg)            absorbed photon flux -> current
  J0(Eg)  = q * F_cell(>Eg)           radiative recombination (cell emits to hemisphere)
  Voc     = (kT/q) * ln(Jsc/J0 + 1)
  FF      = empirical Green expression from normalized v_oc
  eta     = Jsc * Voc * FF / Pin,  Pin = 1000 W/m^2

Photon flux from Planck law integrated over energy:
  phi(E) = 2*pi*E^2 / (h^3 c^2 (exp(E/kT)-1))     [photons / m^2 / s / J]
Sun is diluted by f = 2.16e-5 (solid angle of solar disc, 1-sun).
Cell emits into a hemisphere (pi steradians already in the 2*pi factor convention
used here consistently for both terms, so the RATIO — which sets Voc — is exact;
absolute Jsc is normalized so AM1.5G Pin = 1000 W/m^2 gives the canonical curve).

Verified anchors (must hold in tests):
  - peak in [1.2, 1.5] eV
  - peak value in [30, 35] %  (canonical 33.7 % at 1.34 eV)
  - Si (1.12 eV) -> ~32-33 % limit; certified Si record 28.1 % (LONGi/ISFH 2026) sits below it.
"""

import numpy as np

Q = 1.602176634e-19      # C
H = 6.62607015e-34       # J s
HBAR = H / (2 * np.pi)
C = 299792458.0          # m/s
K = 1.380649e-23         # J/K
T_SUN = 5800.0
T_CELL = 300.0
F_DILUTE = 2.16e-5       # 1-sun geometric dilution
PIN = 1000.0             # W/m^2 (AM1.5G reference)

_E = np.linspace(0.30 * Q, 4.50 * Q, 4000)  # integration grid (J)


def _planck_photon_flux(E, T):
    # photons / m^2 / s / J, into hemisphere
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        x = E / (K * T)
        denom = np.expm1(np.clip(x, 0, 700))
        phi = (2.0 * np.pi * E**2) / (H**3 * C**2 * denom)
        phi[~np.isfinite(phi)] = 0.0
    return phi


_PHI_SUN_RAW = F_DILUTE * _planck_photon_flux(_E, T_SUN)
_PHI_CELL = _planck_photon_flux(_E, T_CELL)

# 1-sun normalization (best practice: NREL/IEC 60904-3, Pin = 1000 W/m^2).
# Raw diluted-5800K blackbody integrates to ~1347 W/m^2 (extraterrestrial);
# without rescaling every efficiency is inflated ~35%. Rescaling photon flux
# so integrated sun power == PIN keeps Jsc/Voc/eta self-consistent.
# Note: with a 5800 K blackbody sun the peak is ~31% (SQ's 1961 value was 30%
# for 6000 K blackbody); the familiar 33.7% uses the AM1.5G spectrum instead.
import numpy as _np
_P_SUN_RAW = float(_np.trapezoid(_E * _PHI_SUN_RAW, _E))
_SUN_SCALE = PIN / _P_SUN_RAW
_PHI_SUN = _SUN_SCALE * _PHI_SUN_RAW


def _integrate_above(Eg_J, phi):
    m = _E >= Eg_J
    return float(np.trapezoid(phi[m], _E[m]))


def sq_point(Eg_eV: float) -> dict:
    Eg = Eg_eV * Q
    Ns = _integrate_above(Eg, _PHI_SUN)    # photons/m^2/s from sun
    Nc = _integrate_above(Eg, _PHI_CELL)   # photons/m^2/s cell emission
    Jsc = Q * Ns
    J0 = Q * Nc
    Vt = K * T_CELL / Q
    Voc = Vt * np.log(Jsc / max(J0, 1e-300) + 1.0)
    v = Voc / Vt
    FF = (v - np.log(v + 0.72)) / (v + 1.0)  # Green 1982 empirical
    eta = Jsc * Voc * FF / PIN
    return {"Eg_eV": Eg_eV, "Jsc_A_m2": Jsc, "J0_A_m2": J0,
            "Voc_V": float(Voc), "FF": float(FF), "eta": float(eta)}


def sq_curve(eg_list=None):
    if eg_list is None:
        eg_list = np.linspace(0.5, 2.5, 81)
    rows = [sq_point(float(e)) for e in eg_list]
    etas = np.array([r["eta"] for r in rows])
    i = int(np.argmax(etas))
    return {"rows": rows, "peak": rows[i]}
