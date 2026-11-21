# Downloads: every model in Python, Zemax OpticStudio and CODE V

> **Written by AI.** These files, and the script that generates them, were written by an AI
> assistant (Claude, by Anthropic) at Dan Gray's direction.

These files are **generated** from the tables in [`data/`](../data) by
[`scripts/make_formats.py`](../scripts/make_formats.py). Never edit them by hand: change the data,
then run `python3 scripts/make_formats.py`. `python3 -m unittest discover tests` reads every Zemax
and CODE V file back in and checks it against the data.

To download one file, open it on GitHub and use the download button, or fetch its raw address, e.g.
`https://raw.githubusercontent.com/Optoguy/EveryEyeModel/main/formats/zemax/arizona-eye-0D.zmx`.

## What is here

| Model | Python / JSON | Zemax OpticStudio | CODE V |
|---|---|---|---|
| Paraxial (reduced) eye, 60 D | [json](json/paraxial-reduced-eye.json) | — | — |
| Le Grand, relaxed | [json](json/le-grand-relaxed.json) | [zmx](zemax/le-grand-relaxed.zmx) | [seq](codev/le-grand-relaxed.seq) |
| Le Grand, accommodated | [json](json/le-grand-accommodated.json) | [zmx](zemax/le-grand-accommodated.zmx) | [seq](codev/le-grand-accommodated.seq) |
| Arizona eye, 0 D | [json](json/arizona-eye-0D.json) | [zmx](zemax/arizona-eye-0D.zmx) | [seq](codev/arizona-eye-0D.seq) |
| Arizona eye, 2 D | [json](json/arizona-eye-2D.json) | [zmx](zemax/arizona-eye-2D.zmx) | [seq](codev/arizona-eye-2D.seq) |
| Arizona eye, 4 D | [json](json/arizona-eye-4D.json) | [zmx](zemax/arizona-eye-4D.zmx) | [seq](codev/arizona-eye-4D.seq) |
| Arizona eye, 6 D | [json](json/arizona-eye-6D.json) | [zmx](zemax/arizona-eye-6D.zmx) | [seq](codev/arizona-eye-6D.seq) |
| Escudero-Sanz and Navarro wide-angle eye | [json](json/escudero-sanz-navarro-wide-angle-eye.json) | [zmx](zemax/escudero-sanz-navarro-wide-angle-eye.zmx) | [seq](codev/escudero-sanz-navarro-wide-angle-eye.seq) |

The paraxial eye has no Zemax or CODE V file: it is one paraxial surface of focal length 16.667 mm
in either program.

## Python

[`python/everyeyemodel.py`](../python/everyeyemodel.py) is one file, standard library only. Copy it
next to your script:

```python
import everyeyemodel as eem
eem.names()                       # the model ids
m = eem.get("le-grand-relaxed")   # title, source, surfaces, stop_surface, notes
eem.arizona(3.5)                  # the Arizona eye at any accommodation, in dioptres
print(eem.to_csv(m))              # the prescription at its primary wavelength
```

Each surface carries `radius_mm`, `conic`, `thickness_mm` (to the next surface), `medium` and
`index`, a dictionary of the index after the surface keyed by wavelength in nanometres. The same
data, one model per file, is in [`json/`](json).

## Zemax OpticStudio (`.zmx`)

- Sequential files, written as OpticStudio writes them (UTF-16, Windows line endings). Open with
  File, Open.
- Object at infinity, field angles in degrees (0, 10 and 20; 0 to 60 for the wide-angle eye), real
  ray aiming.
- **The stop is at the iris (lens front surface)** and its aperture floats with it. Its
  semi-diameter is set to give a **4 mm entrance pupil** at the primary wavelength. Change the stop
  semi-diameter for another pupil.
- **Media are model glasses** (fixed nd and Vd):
  - Arizona: nd and Vd as published.
  - Wide-angle eye: OpticStudio's model glass cannot hold four arbitrary indices. nd and Vd come
    from a two-term Cauchy fit through the four published indices, within 2.6 × 10⁻⁴ of them.
    OpticStudio then applies its own dispersion model, so its indices at 458 and 633 nm will differ
    slightly from the paper. The CODE V file and the JSON carry the exact published indices.
  - Le Grand: the one published index. The model has no dispersion, so the Vd of 50 is only a
    placeholder; use a single wavelength.
- Built from a file layout that loads in OpticStudio 19.4. **These particular files have not yet been
  opened in OpticStudio**; if one fails to load, please open an issue with the version.

## CODE V (`.seq`)

- Run with `IN <file>.seq`. Each file starts a new lens (`LEN NEW`), sets a 4 mm entrance pupil
  (`EPD 4`), the wavelengths and field angles, and ends with `GO`.
- **Media are private glasses** (`PRV` … `END`) with an index at each model wavelength. The
  wide-angle eye's are the published indices exactly. Arizona's at 656.3 and 486.1 nm come from a
  two-term Cauchy fit through nd and Vd. Le Grand's are the single published index at every
  wavelength.
- The stop (`STO`) is on the lens front surface, and conic constants follow `CON` as `K`.
- **These files have not yet been opened in CODE V.** They follow CODE V's sequence-file commands, but
  nobody has run them. If one fails, please open an issue with the error line.

## Checks run on every generation

- The Arizona formulas at A = 0 match `data/arizona-eye-0D.csv`.
- Paraxial power at the primary wavelength: Le Grand 59.94 D, Le Grand accommodated 67.68 D,
  Arizona 0 D 60.62 D, wide-angle eye 60.72 D at 543 nm. These agree with an independent ray tracer.
- The tests read each Zemax and CODE V file back and match every radius, conic, thickness and stop
  position to the data.
