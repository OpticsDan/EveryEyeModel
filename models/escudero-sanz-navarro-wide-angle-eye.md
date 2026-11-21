# Escudero-Sanz and Navarro wide-angle eye (1999)

Navarro's 1985 schematic eye turned into a wide-angle model by adding a curved retina. Four conic
surfaces, with indices given at four wavelengths. Built to reproduce the eye's off-axis aberrations
over a wide field, so it is the right choice when the field of view goes well past 45°.

## Prescription

| # | Surface | Radius (mm) | Conic K | Thickness to next (mm) | Medium after |
|---|---|---|---|---|---|
| 1 | Cornea front | 7.72 | −0.26 | 0.55 | cornea |
| 2 | Cornea back | 6.50 | 0 | 3.05 | aqueous |
| 3 | Lens front | 10.20 | −3.1316 | 4.00 | lens |
| 4 | Lens back | −6.00 | −1.0 | 16.3202 | vitreous |
| 5 | Retina | −12.00 | 0 | — | — |

Axial length: 23.9202 mm (sum of thicknesses).

## Refractive indices

| Medium | 458 nm | 543 nm | 589.3 nm | 632.8 nm |
|---|---|---|---|---|
| Cornea | 1.3828 | 1.3777 | 1.376 | 1.3747 |
| Aqueous | 1.3445 | 1.3391 | 1.3374 | 1.336 |
| Lens | 1.4292 | 1.4222 | 1.42 | 1.4183 |
| Vitreous | 1.3428 | 1.3377 | 1.336 | 1.3347 |

The model's design wavelength is 543 nm.

## Where the stop goes

The iris sits in the aqueous, just in front of the lens. Common implementations place it at the
lens front surface. Size it for the entrance pupil your study needs; the example below uses a
1.5 mm stop semi-diameter.

## Files

- [`data/escudero-sanz-navarro-wide-angle-eye.csv`](../data/escudero-sanz-navarro-wide-angle-eye.csv)

## Sources

- I. Escudero-Sanz and R. Navarro, "Off-axis aberrations of a wide-angle schematic eye model",
  *J. Opt. Soc. Am. A* **16**(8), 1881–1891 (1999),
  [doi:10.1364/JOSAA.16.001881](https://doi.org/10.1364/JOSAA.16.001881).
- R. Navarro, J. Santamaría and J. Bescós, "Accommodation-dependent model of the human eye with
  aspherics", *J. Opt. Soc. Am. A* **2**(8), 1273–1281 (1985),
  [doi:10.1364/JOSAA.2.001273](https://doi.org/10.1364/JOSAA.2.001273), the eye it is built on.
- Values here as implemented in the ZOSPy example "Escudero-Sanz eye model"
  ([documentation](https://zospy.readthedocs.io/en/latest/examples/Escudero-Sanz%20eye%20model/Escudero-Sanz%20eye%20model.html)).
  Checked 2026-11-21. Not yet checked line by line against the 1999 paper itself.
