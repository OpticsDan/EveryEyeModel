# EveryEyeModel

Published schematic eye models, written out as lens prescriptions you can type into a lens design
program.

Every ophthalmoscope, fundus camera or retinal imager design has an eye in it. The model you choose
for that eye decides which questions the design can answer. This repository collects the common
published models in one consistent format, each with its source, so you can pick the right one and
enter it without hunting through papers.

## Which model for which question

| Question | Model to start with |
|---|---|
| First-order layout, pupil positions, magnification | [Paraxial (reduced) eye](models/paraxial-reduced-eye.md) |
| Cardinal points and textbook checks | [Le Grand full theoretical eye](models/le-grand-full-theoretical-eye.md) |
| Clinical levels of aberration; reflections from the cornea and lens; accommodation | [Arizona eye](models/arizona-eye.md) |
| Wide fields, well past 45°, and the eye's off-axis aberrations | [Escudero-Sanz and Navarro wide-angle eye](models/escudero-sanz-navarro-wide-angle-eye.md) |

A practical sequence: lay out and optimise the imaging with a paraxial eye, switch to the Arizona
eye to check reflections against the pupil split, and bring in a wide-angle eye only when the field
or the specification needs it.

## The models

| Model | Surfaces | Aspheric | Dispersion | Accommodation | Files |
|---|---|---|---|---|---|
| Paraxial (reduced) eye | 1 ideal lens | no | no | no | [model](models/paraxial-reduced-eye.md) |
| Le Grand full theoretical eye | 4 | no | no | relaxed and accommodated | [model](models/le-grand-full-theoretical-eye.md), [csv](data/le-grand-full-theoretical-eye.csv), [accommodated csv](data/le-grand-accommodated.csv) |
| Arizona eye | 4 | conic | Abbe numbers | any level, by formula | [model](models/arizona-eye.md), [csv at 0 D](data/arizona-eye-0D.csv) |
| Escudero-Sanz and Navarro wide-angle eye (1999) | 4 + curved retina | conic | indices at 4 wavelengths | no | [model](models/escudero-sanz-navarro-wide-angle-eye.md), [csv](data/escudero-sanz-navarro-wide-angle-eye.csv) |

## Still to add

Each is added once its values are checked against the primary source. Nothing is published here
from memory.

| Model | Why it matters |
|---|---|
| Gullstrand No. 1 exact eye (1909) | The classic six-surface reference, relaxed and accommodated, with a two-shell lens |
| Gullstrand-Emsley eye | A simplified three-surface version, for teaching and first-order checks |
| Pomerantzeff wide-angle eye (1971, 1984) | The first eye built for wide-field fundus imaging; a many-shell lens, about 15 years before the Navarro wide-angle eye |
| Liou and Brennan eye (1997) | Gradient-index lens and a decentred pupil; the anatomical reference |
| Atchison eye (2006) | A gradient-index lens model |
| Goncharov and Dainty eye (2007) | A gradient-index lens model |

Suggestions for more, with a citation, are welcome as issues.

## Contributing

Open an issue or a pull request with the model's prescription and the **primary source** it comes
from (paper, book and table). A new model is merged once a second person has checked its values
against that source.

## Conventions

- Lengths in millimetres. Light travels left to right, from the object to the retina.
- **Radius:** positive when the centre of curvature is to the right of the surface.
- **Thickness:** the axial distance from that surface to the next one, in the medium after it.
- **Conic constant K**, as used by most design programs: sag
  z = c r² / (1 + √(1 − (1 + K) c² r²)), with c = 1/R. K = 0 is a sphere, −1 a paraboloid. Some
  papers quote asphericity Q instead; Q equals K.
- **Index:** of the medium after the surface. The wavelength is stated with each model.
- Each `data/*.csv` file lists the same surfaces as its model page, one row per surface.

## Using a model in a design program

- Enter each medium as a model glass with a fixed index and Abbe number, where the model gives one.
- Put the system stop at the iris, and solve its size for the entrance pupil your study needs. The
  cornea magnifies the iris, so the entrance pupil is larger than the stop.
- The first four surfaces reflect light back out of the eye, giving the Purkinje images. In a
  stray-light study each one is a candidate ghost.
- Where the model has a curved retina, put your field points on that surface, not on a plane.

## Accuracy

Every value here is copied from the source named on its page and was checked against that source
when added. If you find a difference from a primary source, open an issue with the reference. These
are average, idealised eyes: none of them describes a particular person.

## Licence

The prescriptions are published scientific data from the papers and books cited. The text and file
layout in this repository are offered for anyone to use.
