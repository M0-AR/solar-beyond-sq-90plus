"""Certified record anchors (independent labs only) from the 2026 literature sweep.

Every number below was cross-voted across >=2 of: Green et al. Solar Cell
Efficiency Tables v67/v68 (2026), NREL Best Research-Cell chart (Aug 2026),
LONGi/JinkoSolar announcements with ESTI/NREL/SIMIT certification,
pv-magazine / Sciencedaily / Joule coverage, DuckDuckGo-lite fallback fetch.

Single-junction ceiling SQ(1J) ~ 33.7 % is NEVER violated at 300 K / 1-sun:
the 50-60 % Si claim (Delaware/Taizhou 2025) is at 30-50 K under laser
illumination — a different thermodynamic regime, flagged as such.
"""

RECORDS = [
    {"tech": "Si crystalline cell", "eta": 0.281, "source": "Green v68 / ISFH 03-2026 (LONGi n-type HT)",
     "kind": "1J"},
    {"tech": "Perovskite cell", "eta": 0.280, "source": "Green v68 / NPVM 02-2026 (HainanU)",
     "kind": "1J"},
    {"tech": "Perovskite/Si tandem 1cm2", "eta": 0.352, "source": "Green v68 / ESTI 02-2026 (LONGi 2T)",
     "kind": "2J"},
    {"tech": "Perovskite/Si tandem record", "eta": 0.355, "source": "LONGi 2026-07-14 / ESTI",
     "kind": "2J"},
    {"tech": "TOPCon perovskite/Si (Jinko)", "eta": 0.3482, "source": "SIMIT 2026-06-19 (JinkoSolar)",
     "kind": "2J"},
    {"tech": "Si module ceiling (lab)", "eta": 0.264, "source": "Green v68 modules",
     "kind": "1J-module"},
    {"tech": "TPV MIT selective emitter", "eta": 0.40, "source": "MIT TPV >40% (sweep consensus)",
     "kind": "TPV"},
    {"tech": "Singlet-fission QY (solution)", "eta": None, "qy": 1.30,
     "source": "Kyushu/JGU JACS 2026-03-25 (Mo spin-flip + tetracene)",
     "kind": "QY"},
    {"tech": "Quantum-cutting PLQY / EQE", "eta": None, "qy": 1.70, "eqe": 1.172,
     "source": "Joule 2026-07 (CsPbCl3:Yb / c-Si 26.00%)",
     "kind": "QY"},
]

SQ_1J_PEAK = 0.337      # canonical
TANDEM_2J_BOUND = 0.46  # our detailed-balance scan must exceed every 2J record
TANDEM_3J_BOUND = 0.49
LANDSBERG = 0.933
