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

## CODE V files, imported into OpticStudio

**Route:** OpticStudio 26.1 SP4 has no menu or API import of CODE V files, so each `.seq` file was
run through the bundled macro "CodeV to OpticStudio Converter.zpl" (version 2.06.4, 2019), once per
file. Files from `formats/codev/` at commit `59bfb13`; converted lenses kept in a scratch folder only.

| File | Converts | Indices | Surfaces (radius, thickness, conic, stop) | Entrance pupil (mm) | EFLY (mm) | Verdict |
|---|---|---|---|---|---|---|
| le-grand-relaxed | yes | ok | ok, stop on surface 3 | 4.000 | 16.6832 | pass |
| le-grand-accommodated | yes | ok | ok, stop on surface 3 | 4.000 | 14.7761 | pass |
| arizona-eye-0D | yes | ok (3 wavelengths) | ok, stop on surface 3 | 4.000 | 16.4955 | pass |
| arizona-eye-2D | yes | ok (3 wavelengths) | ok, stop on surface 3 | 4.000 | 15.8585 | pass |
| arizona-eye-4D | yes | ok (3 wavelengths) | ok, stop on surface 3 | 4.000 | 15.2775 | pass |
| arizona-eye-6D | yes | ok (3 wavelengths) | ok, stop on surface 3 | 4.000 | 14.7475 | pass |
| escudero-sanz-navarro-wide-angle-eye | yes | ok (4 wavelengths) | ok, stop on surface 3 | 4.000 | 16.4679 at 543 nm | pass |

- **Indices:** every private glass (`PRV`) became an OpticStudio table glass, with the index equal
  to the file's value at every system wavelength (largest difference 2 × 10⁻¹⁶). The wide-angle eye
  therefore matches its expected focal length to 0.0001 mm, closer than the `.zmx` file, whose model
  glasses use OpticStudio's dispersion model.
- **Commands:** none was misread. `PRV`/`PWL`, `CON`/`K`, `STO`, `SO`/`SI`, `REF`, `EPD` and
  `XAN`/`YAN` all came through as intended.
- **The 2019 macro in 26.1:** each run warns that it cannot open a `.zos` template and opens a
  Save As dialog; the conversion still completes (save as `.zmx`). A batch run through `CALLMACRO`
  converted only the first file and saved it under every name, so run it once per file. It writes its
  glass tables into the user's Glasscat folder and re-saves `SAMPLES\LENS.zmx`.

**Not tested:** the CODE V files in CODE V itself, and OpticStudio 19.4, where the `.zmx` layout came
from.
