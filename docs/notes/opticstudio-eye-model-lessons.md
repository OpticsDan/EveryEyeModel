---
title: OpticStudio lessons from loading schematic eyes — EFFL vs EFLY, model glass from tabulated indices, the CODE V converter in 26.1
tags: [zemax, eye-model, tooling, promote-common]
sources:
  - "OpticStudio 26.1 SP4 Professional load tests of seven generated .zmx and seven .seq eye-model files, run 2026-11-21 on Dan Gray's machine; record formats/opticstudio-load-test-2026-11-21.md in this repository"
last_synced: 2026-11-21
confidence: verified
status: active
---

# OpticStudio lessons from loading schematic eyes

> **Written by AI** (Claude, by Anthropic) at Dan Gray's direction, from the test record named above.

1. **EFFL reads long for a system not focused at infinity.** For the accommodated eyes (paraxial
   focus 0.06 to 0.23 mm in front of the image surface for a distant object), the EFFL operand gave
   15.43 mm against an expected 14.78 mm, while EFLY from surface 1 to the last refracting surface
   and a hand paraxial trace both gave 14.776. Check such systems with EFLY over the refracting
   surfaces, not EFFL.
2. **There is no ENPD operand;** the entrance pupil diameter is EPDI. `OCOD("ENPD")` fails.
3. **Floating stop sized from a paraxial trace works:** `FLOA` plus the stop's semi-diameter set to
   (entrance pupil radius) × (paraxial height at the stop for a unit-height axial ray) gave
   EPDI = 4.000 mm in every file.
4. **A medium given at several wavelengths cannot be an exact model glass.** A model glass holds
   only nd and Vd. A two-term Cauchy least-squares fit through four published indices left a residual
   of up to 2.6 × 10⁻⁴, and the focal length came out 0.012 mm off. A CODE V private glass (`PRV`
   with `PWL`) holds every index exactly; imported into OpticStudio it became a table glass and
   matched to 0.0001 mm.
5. **No CODE V import on the menu or API in 26.1.** The bundled macro "CodeV to OpticStudio
   Converter.zpl" (version 2.06.4, 2019) still works:
   - it warns that it cannot open a `.zos` template and opens a Save As dialog; the conversion still
     completes (save as `.zmx`);
   - a batch run through `CALLMACRO` with `CALLSETSTR` converted only the first file and saved it
     under every name; run it once per file;
   - it writes `.ZTG` table glasses into the user's Glasscat folder ("Glass name has been modified")
     and re-saves `SAMPLES\LENS.zmx`.
6. **Generated `.zmx` files load in 26.1** when written UTF-16 with a BOM and CRLF line endings, with
   the neutral `VERS 190731 0 100569` line. Open them read-only, or never commit a re-saved copy:
   OpticStudio writes the licence number into `VERS` on save.
