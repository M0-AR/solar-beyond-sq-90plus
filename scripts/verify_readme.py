"""Verify README.md: every number matches results/*.json; no build-tooling leaks.

Checks:
  1. Key formatted stats from benchmark.json + live_validation.json appear verbatim.
  2. Banned tokens (discovery/build tooling) absent — the README must read as pure science.
  3. Media + showcase + beginner-guide anchors referenced.
  4. No stale numbers from earlier drafts (41.x%, 33.7% as OUR peak, wide-gap claim).

Run: python scripts/verify_readme.py  (exit nonzero on any failure)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(HERE, "results", "benchmark.json")) as f:
    B = json.load(f)
with open(os.path.join(HERE, "results", "live_validation.json")) as f:
    L = json.load(f)
with open(os.path.join(HERE, "README.md")) as f:
    MD = f.read()

fails = []


def need(s, why):
    if s not in MD:
        fails.append(f"MISSING [{why}]: {s!r}")
    else:
        print(f"  ok: {s!r} ({why})")


print("== numbers vs benchmark.json ==")
sq = B["sq_peak"]
need(f"{sq['eta']*100:.1f}%", "SQ peak")
need(f"{sq['Eg_eV']:.2f} eV", "SQ gap")
b2, b3 = B["tandem_2j_best"], B["tandem_3j_best"]
need(f"{b2['eta']*100:.1f}%", "2J bound")
need(f"{b3['eta']*100:.1f}%", "3J bound")
mim, tgt = B["rectenna"]["mim_100ohm_1fF"], B["rectenna"]["target_5ohm_0.05fF"]
need(f"{mim['fc_THz']:.1f} THz", "MIM cutoff")
need(f"{tgt['fc_THz']:.0f} THz", "target cutoff")
fis = B["fission"]["qy130_Eg1.1"]
need(f"{fis['G']:.3f}", "fission G")
sel, bb = B["tpv"]["selective_1500K"], B["tpv"]["blackbody_1500K"]
need(f"{sel['eta']*100:.1f}%", "TPV selective")
need(f"{bb['eta']*100:.1f}%", "TPV blackbody")
need(f"{sel['eta']/bb['eta']:.1f}x", "TPV ratio")
hc_s, hc_f = B["hot_carrier"]["perovskite_150ps"], B["hot_carrier"]["gaAs_0.5ps"]
need(f"{hc_s['harvest_frac']*100:.1f}%", "hot slow harvest")
need(f"{hc_f['harvest_frac']*100:.1f}%", "hot fast harvest")
for s in L["sites"]:
    need(f"{s['kwh_per_kwp_3d_sq']}", f"live sq {s['site']}")
    need(f"{s['kwh_per_kwp_3d_tandem']}", f"live tandem {s['site']}")

print("== banned tooling tokens ==")
BANNED = [r"\bwebsearch\b", r"\bExa\b", r"\bSearXNG\b", r"\bsearxng\b",
          r"\bagent-reach\b", r"\bduckduckgo-lite\b", r"\bMCP\b",
          r"\bOpenAlex\b", r"\bpaper-search\b", r"\bgitmcp\b", r"\bKaggle\b",
          r"\bkaggle\b", r"\bsuperpowers\b", r"\bGSD\b", r"\bHacker News\b",
          r"\bBluesky\b", r"\bPlaywright\b", r"\bplaywright\b"]
for pat in BANNED:
    hits = re.findall(pat, MD)
    if hits:
        fails.append(f"BANNED token {pat}: {len(hits)}x")
print("  ok: no tooling tokens" if not any("BANNED" in x for x in fails) else "  FAIL tokens")

print("== anchors & media ==")
for s in ["demo/demo.gif", "demo/demo.mp4", "preview.html",
          "Beginner guide", "You will know more than most interview candidates",
          "figures/01_sq_curve.png", "results/benchmark.json",
          "scripts/verify_readme.py", "MIT"]:
    need(s, "anchor/media")

print("== stale-number guard ==")
for stale in ["41.86%", "41.9%", "57.87%", "rehabilitated by multiplication",
               "gain peaks for **wide-gap", "too-wide\" cell"]:
    if stale in MD:
        fails.append(f"STALE: {stale!r} still in README")

if fails:
    print("\nFAILURES:")
    for x in fails:
        print(" -", x)
    sys.exit(1)
print("\nREADME VERIFIED: numbers match, no leaks, anchors present")
