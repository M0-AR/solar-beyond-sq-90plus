"""EXP-02: tandem bounds vs certified 2026 records — headroom, no violation."""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from src.tandem import scan_2j, scan_3j
from src.sq_limit import sq_curve
from src.records import RECORDS
s = sq_curve()["peak"]["eta"]; b2 = scan_2j(); b3 = scan_3j()
print(f"1J {s*100:.2f}% | 2J {b2['eta']*100:.2f}% {b2['gaps_eV']} | 3J {b3['eta']*100:.2f}% {b3['gaps_eV']}")
for r in RECORDS:
    if r.get("eta"):
        verdict = "BELOW 2J bound (consistent)" if r["eta"] < b2["eta"] else "VIOLATION"
        print(f"  {r['tech']}: {r['eta']*100:.2f}% [{r['source']}] -> {verdict}")
        assert r["eta"] < (b2["eta"] if r["kind"] == "2J" else 0.90)
print("EXP-02 PASS")
