# OpticStudio load test, 2026-11-21

> **Written by AI.** The test was run by an AI assistant (Claude, by Anthropic) at Dan Gray's
> direction, on his OpticStudio machine. This record was written by AI from its result.

**Software:** OpticStudio 26.1 SP4 Professional, through the ZOS-API (standalone). Files from
`formats/zemax/` at commit `8504cd6`, opened read-only and never saved.

**Method:** each file loaded; EFFL operand; EFLY from surface 1 to the last refracting surface;
entrance pupil diameter (EPDI); a real-ray trace of the chief ray and the four marginal rays
(pupil coordinates ±1) at every field, counting ray errors and vignetted rays.

| File | Loads | EFFL (mm) | EFLY (mm) | Expected (mm) | Entrance pupil (mm) | Ray errors / vignetted | Verdict |
|---|---|---|---|---|---|---|---|
| le-grand-relaxed | yes | 16.6832 | 16.6832 | 16.683 | 4.0000 | 0 / 0 | pass |
| le-grand-accommodated | yes | 15.4320 | 14.7761 | 14.776 | 4.0000 | 0 / 0 | pass on EFLY |
| arizona-eye-0D | yes | 16.4963 | 16.4955 | 16.495 | 4.0000 | 0 / 0 | pass |
| arizona-eye-2D | yes | 16.0663 | 15.8585 | 15.859 | 4.0000 | 0 / 0 | pass on EFLY |
| arizona-eye-4D | yes | 15.6654 | 15.2775 | 15.278 | 4.0000 | 0 / 0 | pass on EFLY |
| arizona-eye-6D | yes | 15.2922 | 14.7475 | 14.748 | 4.0000 | 0 / 0 | pass on EFLY |
| escudero-sanz-navarro-wide-angle-eye (543 nm) | yes | 16.4604 | 16.4561 | 16.468 ± 0.05 | 4.0002 | 0 / 0 | pass |

Tolerance: ±0.005 mm, except ±0.05 mm for the wide-angle eye, whose model glasses use
OpticStudio's own dispersion model.

**Observations**

1. The EFFL operand differs from the expected focal length only for the accommodated eyes. For an
   object at infinity their paraxial focus lies 0.06 to 0.23 mm in front of the image surface. The
   loaded surfaces match the files exactly, and EFLY over the eye's surfaces and a hand paraxial
   trace both give the expected values. Use EFLY to check an accommodated eye.
2. OpticStudio has no ENPD operand; the entrance pupil diameter is EPDI.
3. The VERS line in every file is the neutral form. Nothing was saved, so nothing needed scrubbing.

**Not tested:** the CODE V files (no CODE V licence), and OpticStudio 19.4, where the file layout
came from.
