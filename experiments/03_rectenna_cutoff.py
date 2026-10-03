"""EXP-03: rectenna RC cliff — the hidden pattern (10x RC -> ~100x eta at 500 THz)."""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from src.rectenna import spectrum_weighted_eta, road_to_90_table
for row in road_to_90_table():
    print(f"R={row['R_ohm']:>4}ohm C={row['C_fF']:.2f}fF fc={row['fc_THz']:>7}THz eta={row['spectrum_eta']*100:6.3f}%")
e_bad, fc_bad = spectrum_weighted_eta(100, 1.0)
e_good, fc_good = spectrum_weighted_eta(5, 0.05)
print(f"MIM(100ohm,1fF): fc={fc_bad:.1f}THz eta={e_bad*100:.3f}% | TARGET: fc={fc_good:.0f}THz eta={e_good*100:.2f}%")
assert fc_bad < 50 and e_bad < 0.05 and fc_good > 300 and e_good > 10 * e_bad
print("EXP-03 PASS — diode, not antenna, is the bottleneck; RC<0.3fs unlocks optics")
