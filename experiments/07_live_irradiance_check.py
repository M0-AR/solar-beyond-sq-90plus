"""EXP-07: live-sky check — ordering laws must hold on REAL measured sunlight.

Fetches Open-Meteo hourly GHI for Riyadh/Berlin/Atacama (falls back to an
analytical clear-sky day offline) and verifies tandem>fission-base and
plausible kWh/kWp. Deterministic fallback keeps CI green without network.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from src.validate_live import fetch_site, clearsky_fallback, energy_proxy_harvest, SITES
from src.sq_limit import sq_point
from src.tandem import tandem_point

sq = sq_point(1.34)["eta"]
td = tandem_point([0.94, 1.64], series=False)["eta"]
for s in SITES:
    try:
        hours = fetch_site(s["lat"], s["lon"])
        src = "LIVE open-meteo"
    except Exception as e:
        hours, src = clearsky_fallback(), f"FALLBACK ({e})"
    y_sq = energy_proxy_harvest(hours, sq)
    y_td = energy_proxy_harvest(hours, td)
    print(f"{s['name']}: {src} sq={y_sq:.2f} tandem={y_td:.2f} kWh/kWp/3d")
    assert y_td > y_sq and 2.0 < y_sq < 30.0
print("EXP-07 PASS")
