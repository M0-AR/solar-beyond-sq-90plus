"""EXP-04: fission gain — narrow-gap hosts win (verified hidden pattern)."""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from src.singlet_fission import fission_gain
for qy in (1.30, 1.70, 2.00):
    print(f"--- QY={qy*100:.0f}% (anchors: 130% Kyushu2026 solution, 170% CsPbCl3:Yb PLQY) ---")
    for Eg in (1.12, 1.34, 1.70, 1.90):
        r = fission_gain(Eg, qy=qy)
        print(f"  host {Eg:.2f}eV: hot_frac={r['hot_frac']*100:5.1f}% G={r['G']:.3f} "
              f"SQ={r['sq_base']*100:5.2f}% -> ideal {r['eta_ideal']*100:5.2f}% derated {r['eta_derated']*100:5.2f}%")
assert fission_gain(1.1, 1.3)["G"] > fission_gain(1.9, 1.3)["G"]
assert fission_gain(1.1, 1.3)["eta_ideal"] > fission_gain(1.1, 1.3)["sq_base"]
print("EXP-04 PASS — gain peaks at narrow gaps: fission belongs on Si, not wide hosts")
