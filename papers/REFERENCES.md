# Primary sources — every claim in this repo traces to at least two of these.
# "Voting": websearch + duckduckgo + openresearch + paper-search + agent-reach
# + kaggle + wiki + gsd + webfetch-duckduckgo-lite all agreed on these anchors.

## Certified efficiency tables & charts (ground truth for records)
- Green, Dunlop, Yoshita, Kopidakis, Bothe et al. "Solar cell efficiency tables
  (Version 67)" Prog. Photovolt. 2026-01-28. / "(Version 68)" Joule 2026-07-15
  (cell.com/joule/fulltext/S2542-4351(26)00178-9): Si 28.1% (LONGi/ISFH),
  perovskite 26.9-28.0%, perovskite/Si 35.2% ESTI (LONGi 2T), modules 26.4%.
- NREL Best Research-Cell Efficiency Chart, rev 2026-08-14 (nrel.gov/pv/cell-efficiency):
  multijunction families, hybrid-tandem category, 6-J 39.5% concentrator top.
- LONGi 2026-07-14: perovskite/Si 35.5% ESTI-certified world record.
- JinkoSolar 2026-06-19: TOPCon perovskite/Si 34.82% (SIMIT/CAS).
- Oxford PV Brandenburg line: 26.9% tandem module (Fraunhofer CalLab).

## Singlet fission / MEG / quantum cutting (QY > 100% voted)
- Kyushu Univ. / JGU Mainz, JACS 2026-03-25: Mo spin-flip complex + tetracene,
  ~130% quantum yield in solution (Sciencedaily 2026-03-28; TechBriefs).
- Cheng et al., Joule 2026-07-14: CsPbCl3:Yb site-occupancy engineering,
  PLQY 170%, EQE 117.2% @380nm, c-Si device 26.00% (ref 25.58%).
- Rao & Friend, Nature Rev. Mater. 2017: fission to break SQ (455+ cites).
- Tabachnyk et al. 2013: pentacene triplet diffusion 40nm, fission QY 180±15%.
- Baldo, Ekins-Daukes et al., ACS Energy Lett. 2025-09: fission as scalable
  path past the 29.4% Si single-junction practical limit.
- U. Delaware / Taizhou Univ., Nano-Micro Lett. 2025-09: 50-60% Si at 30-50K
  under laser light (cryogenic regime — NOT a 300K/1-sun SQ violation).

## Rectennas / THz diodes (cutoff law voted)
- Zhu, Joshi, Pelz, Moddel 2013: optical-rectenna overview (MIM to ~150 THz max).
- Reynaud et al. 2020 (Prog. Quant. Electron.): rectifying antennas µwave→visible.
- Citroni et al. 2022 (Nanomaterials): THz rectifier review, 28.3 THz MIM demos.
- Bhateja 2024 (Preprints review): Optical Rectennas — fabrication limits in THz.
- RWTH 1034240: graphene THz diodes (responsivity/resistance/cutoff figures).
- IEEE Spectrum: world-record optical rectenna still ~100x below needs for solar.

## TPV / photon recycling (selective-emitter + Landsberg voted)
- Suemitsu, Asano, Inoue, Noda, arXiv 1906.05727: Si-rod photonic-crystal TPV,
  11.2% @1338K (1.65x prior record) — our blackbody-anchor neighborhood.
- Tong et al. 2015: thin-film thermal-well emitters, Ge/GaSb 38.7% near-field.
- Molesky & Jacob 2015: ideal near-field TPV via matched van Hove singularities.
- Datas & Vaillon 2019: thermionic-enhanced near-field TPV, 30% + 70 W/cm² @2000K/100nm.
- Feng et al. 2021: photon chemical potential profiles in near-field TPV.
- Nimje et al., arXiv 2509.16048: substrate engineering beats power-efficiency tradeoff.
- MIT consensus (sweep): selective-emitter TPV >40% (turbine competitor).
- Landsberg 93.3% = far-field thermodynamic ceiling for photon-recycling engines.

## Hot carriers (slow-cooling window voted)
- Sci. Direct 2026-07 review: hot-carrier dynamics in metal-halide perovskites.
- RSC Chem. Sci. 2026-05: intraband-trap-state engineering slows FAPbI3 cooling.
- RSC Chem. Soc. Rev. 2026-03: optical probes of perovskite hot carriers.
- Nozik 2021 (J. Chem. Phys.): quantization + fission paths past thermalization losses.
- Ross-Nozik 66% (max concentration) / ~50%+ 1-sun realistic-contact bound.

## Live / field data used for verification
- Open-Meteo forecast API (hourly shortwave_radiation, no key): Riyadh/Berlin/Atacama.
- Kaggle solar datasets (manifest): 350 kWp ground-mount plant; Gujarat inverter
  dataset; 2.26 MW digital-twin demo — PR 0.75-0.85 sanity band for yields.
- UNSW outdoor field study (pv-magazine 2026-10-01): commercial perovskite/tandem
  modules under test — module-gap evidence (lab 35% → module ~26-29%).

## Benchmarking best practice (method voted)
- NREL measurement rules: IEC 60904-3 / ASTM G173 spectra, 25 °C, aperture/total
  area, independent-lab confirmation before any record claim.
- Reproducibility: pinned deps, Docker, seeded RNG, JSON artifacts, CI physics tests.
