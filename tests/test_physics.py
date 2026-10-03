"""Physics regression tests — every law the paper claims is asserted here."""
from src.sq_limit import sq_curve, sq_point
from src.tandem import scan_2j, scan_3j
from src.rectenna import spectrum_weighted_eta, cutoff_freq_THz
from src.singlet_fission import fission_gain
from src.tpv import tpv_point, near_field_boost, landsberg_limit
from src.hot_carrier import hot_carrier_eta


def test_sq_peak_matches_canon():
    p = sq_curve()["peak"]
    # 5800 K blackbody sun -> ~31% (SQ 1961: 30% for 6000 K blackbody;
    # the familiar 33.7% uses the AM1.5G spectrum, not blackbody)
    assert 1.15 <= p["Eg_eV"] <= 1.40
    assert 0.28 <= p["eta"] <= 0.33


def test_si_record_below_sq():
    si = sq_point(1.12)["eta"]
    assert si > 0.281  # certified 28.1% must not violate limit


def test_tandem_bounds_ordered():
    s = sq_curve()["peak"]["eta"]
    b2 = scan_2j()["eta"]
    b3 = scan_3j()["eta"]
    assert 0.42 <= b2 <= 0.48 and 0.46 <= b3 <= 0.54
    assert b2 > s and b3 > b2
    assert b2 < 0.90  # junctions alone never reach 90%


def test_rectenna_cutoff_law():
    assert cutoff_freq_THz(100, 1.0) < 50      # MIM far below optical
    assert cutoff_freq_THz(5, 0.05) > 300      # target reaches optical
    e_bad, _ = spectrum_weighted_eta(100, 1.0)
    e_good, _ = spectrum_weighted_eta(5, 0.05)
    assert e_bad < 0.05 and e_good > 10 * e_bad


def test_fission_gain_hidden_pattern():
    g130 = fission_gain(1.7, qy=1.30)["G"]
    g170 = fission_gain(1.7, qy=1.70)["G"]
    assert g130 > 1.0 and g170 > g130
    # VERIFIED direction: narrow-gap hosts gain more (large 2Eg blue fraction);
    # fission flattens the SQ peak instead of moving it to wide gaps.
    assert fission_gain(1.1, qy=1.30)["G"] > fission_gain(1.9, qy=1.30)["G"]
    ideal = fission_gain(1.1, qy=1.30)
    assert ideal["eta_ideal"] > ideal["sq_base"]  # gain beats bare SQ at same gap
    assert ideal["eta_derated"] < 0.933


def test_tpv_selective_and_landsberg():
    from src.tpv import scan_temperature, tpv_point as _tp
    scan = scan_temperature()
    for r in scan:  # co-designed selective beats blackbody at EVERY temperature
        bb = _tp(r["Eg_eV"], r["Te_K"], delta=10.0, suppr=1.0)["eta"]
        assert r["eta"] > bb
    mid = next(r for r in scan if r["Te_K"] == 1500)
    bb1500 = _tp(0.72, 1500, delta=10.0, suppr=1.0)["eta"]
    assert mid["eta"] / bb1500 > 3.0
    assert scan[-1]["eta"] >= scan[0]["eta"]
    assert near_field_boost(10) > 100 > near_field_boost(1000)
    assert abs(landsberg_limit() - 0.933) < 1e-12


def test_hot_carrier_window():
    slow = hot_carrier_eta(1.4, 150.0)
    fast = hot_carrier_eta(1.4, 0.5)
    assert slow["harvest_frac"] > 0.9 > fast["harvest_frac"]
    assert slow["eta_hot"] < 0.90
