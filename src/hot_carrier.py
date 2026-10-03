"""Hot-carrier model: extraction race between cooling and collection.

Excess photon energy E - Eg becomes carrier kinetic energy ("heat").
Conventional cell: cools in tau_cool ~ 0.1-1 ps (phonon emission) -> lost.
Hot-carrier cell: extracts through energy-selective contacts in tau_ext;
fraction harvested = 1 / (1 + tau_ext / tau_cool_eff).

Anchors from our 2026 sweep (halide perovskites slow-cooling reviews):
  - GaAs bulk:            tau_cool ~   0.5 ps
  - FAPbI3 engineered ITS: tau_cool ~  50-200 ps (slowed 100x)
  - PeQD bottleneck:       tau_cool ~ 100+ ps
  - Selective-contact target: tau_ext ~ 1-10 ps
So perovskites open a real extraction window (tau_cool >> tau_ext) where
GaAs does not. Even partial extraction lifts the single-junction ceiling
from 33.7 % toward 50-66 % (Ross-Nozik limit 66 % at max concentration;
~50 %+ at 1-sun with realistic contacts). It cannot alone reach 90 % —
the benchmark proves that — but it stacks with fission/TPV concepts.

Verified relations:
  - harvested fraction increases monotonically as tau_cool grows
  - GaAs-like (0.5 ps) harvests < 10 % of excess with 10 ps contacts
  - perovskite-like (150 ps) harvests > 90 % under the same contacts
"""

import numpy as np
from .sq_limit import sq_point


def harvest_fraction(tau_cool_ps: float, tau_ext_ps: float = 10.0) -> float:
    return float(1.0 / (1.0 + tau_ext_ps / max(tau_cool_ps, 1e-9)))


def hot_carrier_eta(Eg_eV=1.4, tau_cool_ps=150.0, tau_ext_ps=10.0,
                    excess_share=0.35) -> dict:
    """excess_share = fraction of incident solar energy arriving as above-gap
    excess (depends on Eg; ~0.3-0.4 for Eg 1.1-1.5 eV under sun)."""
    base = sq_point(Eg_eV)
    f = harvest_fraction(tau_cool_ps, tau_ext_ps)
    # recovered excess adds to output (upper bound, contact voltage cost 0.9)
    eta = base["eta"] + excess_share * f * 0.9 * (1.0 - base["eta"])
    return {"Eg_eV": Eg_eV, "tau_cool_ps": tau_cool_ps,
            "tau_ext_ps": tau_ext_ps, "harvest_frac": f,
            "sq_base": base["eta"], "eta_hot": float(min(eta, 0.66))}


def cooling_ladder(Eg_eV=1.4):
    out = []
    for tau in [0.5, 2, 10, 50, 150, 500]:
        out.append(hot_carrier_eta(Eg_eV, tau_cool_ps=float(tau)))
    return out
