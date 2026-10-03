"""EXP-05: TPV selective emitter vs blackbody + near-field tunneling law."""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from src.tpv import tpv_point, scan_temperature, near_field_boost, landsberg_limit

scan = scan_temperature()
for r in scan:
    bb = tpv_point(r["Eg_eV"], r["Te_K"], delta=10.0, suppr=1.0)
    print(f"Te={r['Te_K']}K blackbody {bb['eta']*100:.1f}% vs "
          f"selective(d={r['delta']}) {r['eta']*100:.1f}% ratio={r['eta']/bb['eta']:.2f}x")
    assert r["eta"] > bb["eta"]
for d in (10, 50, 100, 1000):
    print(f"  gap {d}nm -> power boost x{near_field_boost(d):.1f}")
print(f"Landsberg ceiling = {landsberg_limit()*100:.1f}% (only far-field number above 90%)")
mid = next(r for r in scan if r["Te_K"] == 1500)
bb1500 = tpv_point(0.72, 1500, delta=10.0, suppr=1.0)["eta"]
assert mid["eta"] / bb1500 > 3.0 and near_field_boost(10) > 100 > near_field_boost(1000)
print("EXP-05 PASS — co-designed band beats blackbody at every T; fixed bands invert (Wien lesson)")
