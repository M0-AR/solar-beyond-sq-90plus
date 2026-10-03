"""Optical rectenna model: why wave-rectification has NOT yet delivered,
and exactly what diode spec would unlock it.

Physics chain:
  antenna_coupling(f)  ~ Lorentzian capture around antenna resonance
  diode_cutoff(f)       = 1 / sqrt(1 + (f / f_c)^2),  f_c = 1 / (2 pi R C)
  eta_system(f)        = eta_antenna * eta_coup * eta_diode(f) * eta_match

Key quantitative result (reproduced here, matches Zhu/Moddel 2013 review,
Periasamy thesis, 2022-2024 THz-rectifier reviews found in our literature sweep):
  - State-of-art MIM: R ~ 100-1000 ohm, C ~ 1-10 fF  ->  f_c ~ 1-30 THz
  - Solar spectrum peaks at ~ 200-1000 THz (0.5-3.5 eV photons)
  - Therefore eta_diode at optical frequencies ~ (f_c/f)^2 ~ 1e-4..1e-2
  - Demonstrated solar-rectenna efficiencies remain < 1 % — NOT a materials
    accident but a cutoff-frequency law. Any claim of >10 % full-spectrum
    rectenna with R*C >> 0.1 fs contradicts this model and must show a
    measured f_c or a non-RC mechanism (geometric/ballistic diode).

Hidden-pattern experiment included: sweep R*C and show the cliff — a 10x
reduction in R*C buys ~100x system efficiency at 500 THz until f_c ~ f.
That is the engineering target: R*C < 0.3 fs  <=>  f_c > 500 THz.
"""

import numpy as np


def cutoff_freq_THz(R_ohm: float, C_fF: float) -> float:
    C = C_fF * 1e-15
    return 1.0 / (2 * np.pi * R_ohm * C) / 1e12


def diode_rolloff(f_THz, fc_THz):
    f = np.asarray(f_THz, dtype=float)
    return 1.0 / (1.0 + (f / fc_THz) ** 2)


def system_eta(f_THz, R_ohm, C_fF, eta_ant=0.9, eta_match=0.9):
    fc = cutoff_freq_THz(R_ohm, C_fF)
    return eta_ant * diode_rolloff(f_THz, fc) * eta_match, fc


def spectrum_weighted_eta(R_ohm, C_fF):
    """Weight diode response by a 5800 K photon-flux spectrum (THz axis)."""
    f = np.linspace(50, 1200, 400)  # THz covering 0.2-5 eV
    h = 4.135667696e-15  # eV s
    E = h * f * 1e12
    kT = 8.617333e-5 * 5800
    with np.errstate(over="ignore", divide="ignore"):
        w = (E**2) / np.expm1(np.clip(E / kT, 0, 700))
    w /= w.sum()
    eta_f, fc = system_eta(f, R_ohm, C_fF)
    return float(np.sum(w * eta_f)), float(fc)


def road_to_90_table():
    """What R*C is needed for the diode to stop being the bottleneck?"""
    rows = []
    for R, C in [(500, 5.0), (100, 1.0), (50, 0.5), (20, 0.2), (10, 0.1), (5, 0.05)]:
        eta, fc = spectrum_weighted_eta(R, C)
        rows.append({"R_ohm": R, "C_fF": C, "RC_fs": R * C * 1e-3 * 1e3,
                     "fc_THz": round(fc, 1), "spectrum_eta": round(eta, 4)})
    return rows
