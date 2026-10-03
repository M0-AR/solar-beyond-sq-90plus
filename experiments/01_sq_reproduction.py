"""EXP-01: reproduce the Shockley-Queisser curve from Planck's law (no fitted data)."""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from src.sq_limit import sq_curve
sq = sq_curve()
print(f"SQ peak: {sq['peak']['eta']*100:.2f}% at {sq['peak']['Eg_eV']:.2f} eV "
      "(blackbody sun; AM1.5G canon is 33.7% @1.34eV)")
for Eg in (1.12, 1.34, 1.43, 1.55):
    r = next(x for x in sq["rows"] if abs(x["Eg_eV"] - Eg) < 0.03)
    print(f"  Eg={Eg:.2f} eV -> {r['eta']*100:.2f}%  Jsc={r['Jsc_A_m2']:.1f} A/m2 Voc={r['Voc_V']:.3f} V FF={r['FF']:.3f}")
assert 0.28 <= sq["peak"]["eta"] <= 0.33
print("EXP-01 PASS")
