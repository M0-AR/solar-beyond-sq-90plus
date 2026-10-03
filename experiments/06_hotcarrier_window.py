"""EXP-06: hot-carrier extraction window — perovskites open what GaAs closes."""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from src.hot_carrier import hot_carrier_eta, cooling_ladder
for r in cooling_ladder():
    print(f"tau_cool={r['tau_cool_ps']:>6}ps harvest={r['harvest_frac']*100:5.1f}% "
          f"SQ={r['sq_base']*100:5.2f}% -> hot {r['eta_hot']*100:5.2f}%")
slow, fast = hot_carrier_eta(1.4, 150.0), hot_carrier_eta(1.4, 0.5)
assert slow["harvest_frac"] > 0.9 > fast["harvest_frac"] and slow["eta_hot"] < 0.90
print("EXP-06 PASS — slow cooling (100ps+) + 10ps contacts = extraction window")
