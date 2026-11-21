---
title: Schematic eye models — prescriptions, sources and which to use
tags: [optics, eye-model, reference, promote-common]
sources:
  - "J. Schwiegerling, 'Schematic Eyes and Ametropia', OPTI course notes, Visual Optics Lab, University of Arizona (PDF, wp.optics.arizona.edu), read 2026-11-21: Le Grand relaxed and accommodated, Arizona eye with accommodation formulas"
  - "J. Schwiegerling, Field Guide to Visual and Ophthalmic Optics (SPIE Press, 2004): Arizona eye, as published"
  - "I. Escudero-Sanz and R. Navarro, J. Opt. Soc. Am. A 16(8), 1881-1891 (1999): wide-angle eye; values as in the ZOSPy example implementation, not yet checked against the paper"
  - "Paraxial values computed 2026-11-21 by two independent ray tracers, both agreeing with OpticStudio 26.1 SP4"
last_synced: 2026-11-21
confidence: verified
status: active
---

# Schematic eye models

> **Written by AI** (Claude, by Anthropic) at Dan Gray's direction, from the sources above.

Lengths in mm. Radius positive when its centre is towards the retina. Conic K (Q in some papers;
sag z = c r² / (1 + √(1 − (1 + K) c² r²))). Index of the medium after the surface. The stop (iris) is
at the lens front surface in every model here.

## Which model for which question

| Question | Model |
|---|---|
| First-order layout, pupils, magnification | Paraxial eye: one ideal 60 D lens, f = 16.667 mm in air |
| Cardinal points, textbook checks | Le Grand full theoretical eye |
| Clinical levels of aberration, reflections, accommodation | Arizona eye |
| Fields well past 45°, off-axis aberration | Escudero-Sanz and Navarro wide-angle eye |

## Le Grand full theoretical eye (one set of indices, no dispersion)

| Surface | Relaxed R | t to next | Accommodated R | t to next | n after |
|---|---|---|---|---|---|
| Cornea front | 7.8 | 0.55 | 7.8 | 0.55 | 1.3771 |
| Cornea back | 6.5 | 3.05 | 6.5 | 2.65 | 1.3374 |
| Lens front | 10.2 | 4.0 | 6.0 | 4.50 | 1.42 (relaxed), 1.4270 (accommodated) |
| Lens back | −6.0 | 16.59655 | −5.5 | 16.497 | 1.336 |
| Retina | −13.4 | | −13.4 (relaxed value; source gives none) | | |

All surfaces spherical. Power 59.94 D relaxed, 67.68 D accommodated.

## Arizona eye (A = accommodation in dioptres)

| Surface | R | K | t to next | Medium | nd | Vd |
|---|---|---|---|---|---|---|
| Cornea front | 7.8 | −0.25 | 0.55 | cornea | 1.377 | 57.1 |
| Cornea back | 6.5 | −0.25 | 2.97 − 0.04A | aqueous | 1.337 | 61.3 |
| Lens front | 12.0 − 0.4A | −7.518749 + 1.285720A | 3.767 + 0.04A | lens | 1.42 + 0.00256A − 0.00022A² | 51.9 |
| Lens back | −5.224557 + 0.2A | −1.353971 − 0.431762A | 16.713 | vitreous | 1.336 | 61.1 |
| Retina | −13.4 | 0 | | | | |

The axial length stays 24.000 mm at every A. Power 60.62 D at A = 0 (587.6 nm). The far point
follows −A to within 0.06 D from 0 to 8 D.

## Escudero-Sanz and Navarro wide-angle eye (1999)

| Surface | R | K | t to next | Medium |
|---|---|---|---|---|
| Cornea front | 7.72 | −0.26 | 0.55 | cornea |
| Cornea back | 6.50 | 0 | 3.05 | aqueous |
| Lens front | 10.20 | −3.1316 | 4.00 | lens |
| Lens back | −6.00 | −1.0 | 16.3202 | vitreous |
| Retina | −12.00 | 0 | | |

| Medium | 458 nm | 543 nm | 589.3 nm | 632.8 nm |
|---|---|---|---|---|
| Cornea | 1.3828 | 1.3777 | 1.376 | 1.3747 |
| Aqueous | 1.3445 | 1.3391 | 1.3374 | 1.336 |
| Lens | 1.4292 | 1.4222 | 1.42 | 1.4183 |
| Vitreous | 1.3428 | 1.3377 | 1.336 | 1.3347 |

Design wavelength 543 nm: paraxial focus exactly on the retina there. Power 60.72 D at 543 nm.
Chromatic focus shift about 1.2 D from 458 to 633 nm.

## Focal lengths in air, for checking an entered model

EFLY from surface 1 to the last refracting surface, primary wavelength: Le Grand relaxed 16.683,
accommodated 14.776; Arizona 0 D 16.495, 2 D 15.859, 4 D 15.278, 6 D 14.748; wide-angle eye
16.468 (543 nm). A 4 mm entrance pupil needs an iris of about 3.53 to 3.59 mm diameter
(cornea magnification about 1.13).

## Not checked

The wide-angle eye's values against the 1999 paper itself. Gullstrand No. 1, Gullstrand-Emsley and
Liou-Brennan are not included: no source with their full tables was read.
