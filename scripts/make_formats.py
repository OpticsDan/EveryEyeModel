#!/usr/bin/env python3
"""Generate the downloadable formats from the prescriptions in data/.

    python3 scripts/make_formats.py           write every file under formats/ and python/
    python3 scripts/make_formats.py --check   exit 1 if any generated file is stale

Standard library only. The data/*.csv files are the source; everything this script writes is
generated and should never be edited by hand. The Arizona eye's accommodation formulas are held here
(from models/arizona-eye.md); at A = 0 they are checked against data/arizona-eye-0D.csv on every run.

Outputs, per model:
  formats/json/<id>.json     the prescription, indices at each wavelength, stop and source
  formats/zemax/<id>.zmx     an OpticStudio sequential file (UTF-16, as OpticStudio writes it)
  formats/codev/<id>.seq     a CODE V sequence file with one private glass per medium
  python/everyeyemodel.py    one importable module holding every model, plus arizona(A)
"""
import csv
import io
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EPD_MM = 4.0  # entrance pupil diameter the stop is sized for in the Zemax and CODE V files

D, F, C = 0.5876, 0.4861, 0.6563  # d, F and C lines, micrometres

SOURCES = {
    "legrand": ("Y. Le Grand and S. G. El Hage, Physiological Optics (Springer, 1980); values as "
                "tabulated in J. Schwiegerling, 'Schematic Eyes and Ametropia', University of Arizona "
                "course notes. See models/le-grand-full-theoretical-eye.md."),
    "arizona": ("J. Schwiegerling, Field Guide to Visual and Ophthalmic Optics (SPIE Press, 2004); values "
                "as tabulated in his University of Arizona course notes. See models/arizona-eye.md."),
    "navarro": ("I. Escudero-Sanz and R. Navarro, J. Opt. Soc. Am. A 16(8), 1881-1891 (1999); values as in "
                "the ZOSPy example implementation, not yet checked against the paper. See "
                "models/escudero-sanz-navarro-wide-angle-eye.md."),
    "paraxial": "The standard 60 D reduced eye. See models/paraxial-reduced-eye.md.",
}


# ---------------------------------------------------------------- dispersion helpers
def cauchy_from_abbe(nd, vd):
    """Two-term Cauchy n = A + B / lambda^2 meeting n(d) = nd and n(F) - n(C) = (nd - 1) / vd."""
    B = ((nd - 1) / vd) / (1 / F ** 2 - 1 / C ** 2)
    A = nd - B / D ** 2
    return A, B


def cauchy_fit(points):
    """Least-squares two-term Cauchy through [(lambda_um, n), ...]; returns (A, B, max residual)."""
    xs = [1 / w ** 2 for w, _ in points]
    ys = [n for _, n in points]
    k = len(xs)
    mx, my = sum(xs) / k, sum(ys) / k
    B = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    A = my - B * mx
    res = max(abs(A + B * x - y) for x, y in zip(xs, ys))
    return A, B, res


def r6(x):
    return float("%.6f" % x)


# ---------------------------------------------------------------- reading the data
def read_csv(name):
    with open(DATA / name, newline="") as f:
        return list(csv.DictReader(f))


def surf(row, index):
    t = row["thickness_mm"]
    return {"name": row["name"].capitalize(), "radius_mm": float(row["radius_mm"]),
            "conic": float(row["conic_K"]), "thickness_mm": float(t) if t else None,
            "medium": row["medium_after"] or None, "index": index}


def le_grand(csv_name, model_id, title):
    rows = read_csv(csv_name)
    waves = [D]
    surfaces = [surf(r, {"587.6": float(r["index_after"])} if r["index_after"] else None) for r in rows]
    return {"id": model_id, "title": title, "source": SOURCES["legrand"], "wavelengths_nm": [587.6],
            "primary_nm": 587.6, "stop_surface": 3, "surfaces": surfaces,
            "notes": ["The source gives one set of indices and no wavelength; they are filed at 587.6 nm. "
                      "The model has no dispersion: use one wavelength.",
                      "The stop (iris) is placed at the lens front surface."]
                     + (["The source gives no retina for the accommodated eye; the relaxed eye's retina "
                         "(R = -13.4 mm) is used."] if "accommodated" in model_id else []),
            "_waves": waves}


ARIZONA_ND_VD = {"cornea": (1.377, 57.1), "aqueous": (1.337, 61.3), "vitreous": (1.336, 61.1)}
ARIZONA_LENS_VD = 51.9


def arizona_rows(A):
    """The Arizona eye at accommodation A (dioptres), from the formulas in models/arizona-eye.md."""
    n_lens = 1.42 + 0.00256 * A - 0.00022 * A * A
    return [
        ("Cornea front", 7.8, -0.25, 0.55, "cornea", 1.377, 57.1),
        ("Cornea back", 6.5, -0.25, 2.97 - 0.04 * A, "aqueous", 1.337, 61.3),
        ("Lens front", 12.0 - 0.4 * A, -7.518749 + 1.285720 * A, 3.767 + 0.04 * A, "lens", n_lens, ARIZONA_LENS_VD),
        ("Lens back", -5.224557 + 0.2 * A, -1.353971 - 0.431762 * A, 16.713, "vitreous", 1.336, 61.1),
        ("Retina", -13.4, 0.0, None, None, None, None),
    ]


def arizona(A):
    waves = [656.3, 587.6, 486.1]
    surfaces = []
    for name, R, K, t, med, nd, vd in arizona_rows(A):
        idx = None
        if nd is not None:
            a, b = cauchy_from_abbe(nd, vd)
            idx = {"%.1f" % w: r6(a + b / (w / 1000) ** 2) for w in waves}
            idx["587.6"] = r6(nd)
        surfaces.append({"name": name, "radius_mm": r6(R), "conic": r6(K),
                         "thickness_mm": None if t is None else r6(t), "medium": med, "index": idx,
                         "nd": None if nd is None else r6(nd), "vd": vd})
    return {"id": "arizona-eye-%gD" % A, "title": "Arizona eye, %g D accommodation" % A,
            "source": SOURCES["arizona"], "wavelengths_nm": waves, "primary_nm": 587.6, "stop_surface": 3,
            "accommodation_D": A, "surfaces": surfaces,
            "notes": ["The model publishes nd and Vd for each medium. Indices at 656.3 and 486.1 nm come from "
                      "a two-term Cauchy fit through nd and Vd: a model of the dispersion, not part of the "
                      "published eye.",
                      "The stop (iris) is placed at the lens front surface."]}


def check_arizona_csv():
    rows = read_csv("arizona-eye-0D.csv")
    for row, (name, R, K, t, med, nd, vd) in zip(rows, arizona_rows(0)):
        assert abs(float(row["radius_mm"]) - R) < 1e-9, row
        assert abs(float(row["conic_K"]) - K) < 1e-9, row
        if t is not None:
            assert abs(float(row["thickness_mm"]) - t) < 1e-9, row
            assert abs(float(row["nd"]) - nd) < 1e-9 and abs(float(row["vd"]) - vd) < 1e-9, row


def navarro():
    rows = read_csv("escudero-sanz-navarro-wide-angle-eye.csv")
    cols = [("458.0", "n_458nm"), ("543.0", "n_543nm"), ("589.3", "n_589_3nm"), ("632.8", "n_632_8nm")]
    surfaces = [surf(r, {k: float(r[c]) for k, c in cols} if r[cols[0][1]] else None) for r in rows]
    return {"id": "escudero-sanz-navarro-wide-angle-eye", "title": "Escudero-Sanz and Navarro wide-angle eye (1999)",
            "source": SOURCES["navarro"], "wavelengths_nm": [458.0, 543.0, 589.3, 632.8], "primary_nm": 543.0,
            "stop_surface": 3, "surfaces": surfaces,
            "notes": ["Indices are published at four wavelengths; the design wavelength is 543 nm.",
                      "The stop (iris) is placed at the lens front surface, as in common implementations."]}


def paraxial():
    f = 1000 / 60
    return {"id": "paraxial-reduced-eye", "title": "Paraxial (reduced) eye, 60 D", "source": SOURCES["paraxial"],
            "wavelengths_nm": [587.6], "primary_nm": 587.6, "stop_surface": 1,
            "surfaces": [{"name": "Ideal lens", "power_D": 60.0, "focal_length_mm": r6(f), "thickness_mm": r6(f),
                          "medium": "air", "index": {"587.6": 1.0}},
                         {"name": "Image plane", "radius_mm": None, "conic": 0.0, "thickness_mm": None,
                          "medium": None, "index": None}],
            "notes": ["One ideal lens in air. Enter it as a paraxial (ideal) surface of focal length "
                      "16.667 mm; there are no Zemax or CODE V files for it here because a paraxial "
                      "surface is one line in either program."]}


def all_models():
    check_arizona_csv()
    ms = [paraxial(),
          le_grand("le-grand-full-theoretical-eye.csv", "le-grand-relaxed", "Le Grand full theoretical eye, relaxed"),
          le_grand("le-grand-accommodated.csv", "le-grand-accommodated", "Le Grand full theoretical eye, accommodated")]
    ms += [arizona(A) for A in (0, 2, 4, 6)]
    ms.append(navarro())
    for m in ms:
        m.pop("_waves", None)
    return ms


# ---------------------------------------------------------------- first order (paraxial y-nu trace)
def n_at(s, nm, prev=1.0):
    if not s["index"]:
        return prev
    return s["index"].get("%.1f" % nm, s["index"].get(str(nm), next(iter(s["index"].values()))))


def paraxial_trace(m, y0, u0, upto=None):
    nm, n, y, u = m["primary_nm"], 1.0, y0, u0
    surfs = [s for s in m["surfaces"] if s["thickness_mm"] is not None]
    for i, s in enumerate(surfs):
        if upto is not None and i == upto:
            return y, u, n
        n2 = n_at(s, nm, n)
        c = 1 / s["radius_mm"]
        u = (n * u - y * (n2 - n) * c) / n2
        n = n2
        if i < len(surfs) - 1:
            y += s["thickness_mm"] * u
    return y, u, n


def power_D(m):
    y, u, n = paraxial_trace(m, 1.0, 0.0)
    return -n * u * 1000


def stop_radius(m, epd):
    """Iris radius giving an entrance pupil of diameter epd: a marginal ray of height epd/2 in air."""
    k = m["stop_surface"] - 1
    # height at the stop's vertex plane for a ray parallel to the axis at height 1
    s = m["surfaces"]
    nm, n, y, u = m["primary_nm"], 1.0, 1.0, 0.0
    for i in range(k):
        n2 = n_at(s[i], nm, n)
        u = (n * u - y * (n2 - n) / s[i]["radius_mm"]) / n2
        n = n2
        y += s[i]["thickness_mm"] * u
    return epd / 2 * y


# ---------------------------------------------------------------- Zemax (.zmx)
def model_glass(s):
    """(nd, vd) for an OpticStudio model glass. Arizona: as published. Navarro: from a Cauchy fit
    through the four published indices. Le Grand: the single index, with a placeholder Vd."""
    if s.get("nd") is not None:
        return s["nd"], s["vd"], None
    pts = [(float(k) / 1000, v) for k, v in s["index"].items()]
    if len(pts) == 1:
        return pts[0][1], 50.0, None
    a, b, res = cauchy_fit(pts)
    nd = a + b / D ** 2
    vd = (nd - 1) / ((a + b / F ** 2) - (a + b / C ** 2))
    return nd, vd, res


def fields_for(m):
    return [0, 20, 40, 60] if m["id"].startswith("escudero") else [0, 10, 20]


def zmx(m):
    waves = m["wavelengths_nm"]
    prim = waves.index(m["primary_nm"]) + 1 if m["primary_nm"] in waves else 1
    fields = fields_for(m)
    r_stop = stop_radius(m, EPD_MM)
    notes = []
    L = ["VERS 190731 0 100569", "MODE SEQ", "NAME %s" % m["title"],
         "NOTE 0 Generated by EveryEyeModel scripts/make_formats.py; stop sized for a %g mm entrance pupil" % EPD_MM,
         "PFIL 0 0 0", "LANG 0", "UNIT MM X W X CM MR CPMM", "FLOA", "ENVD 20 1 0", "GFAC 0 0", "GCAT SCHOTT ",
         "RAIM 0 2 1 1 0 0 0 0 0 1", "PUSH 0 0 0 0 0 0", "SDMA 0 1 0", "OMMA 0 0",
         "FTYP 0 0 %d %d 0 0 0 %d" % (len(fields), len(waves), len(fields)), "ROPD 2", "HYPR 0", "PICB 1",
         "XFLN " + " ".join("0" for _ in fields), "YFLN " + " ".join(str(f) for f in fields),
         "FWGN " + " ".join("1" for _ in fields)]
    for k in ("VDXN", "VDYN", "VCXN", "VCYN", "VANN"):
        L.append(k + " " + " ".join("0" for _ in fields))
    for i in range(24):
        w = waves[i] / 1000 if i < len(waves) else 0.55
        L.append("WAVM %d %s 1" % (i + 1, repr(w)))
    L += ["PWAV %d" % prim, "POLS 1 0 1 0 0 1 0", "GLRS 1 0",
          "GSTD 0 100.000 100.000 100.000 100.000 100.000 100.000 0 1 1 0 0 1 1 1 1 1 1",
          "NSCD 100 500 0 0.001 10 9.9999999999999995e-07 0 0 0 0 0 0 1000000 0 2",
          'COFN QF "COATING.DAT" "SCATTER_PROFILE.DAT" "ABG_DATA.DAT" "PROFILE.GRD"',
          "COFN COATING.DAT SCATTER_PROFILE.DAT ABG_DATA.DAT PROFILE.GRD"]

    def block(n, curv, disz, diam, stop=False, coni=0.0, glas=None, auto=True):
        b = ["SURF %d" % n]
        if stop:
            b.append("  STOP")
        b += ["  TYPE STANDARD", "  FIMP ", '  CURV %.18E 0 0 0 0 ""' % curv, "  HIDE 0 0 0 0 0 0 0 0 0 0",
              "  MIRR 2 0", "  SLAB %d" % (n + 1), "  DISZ %s" % disz]
        if coni:
            b.append("  CONI %r" % coni)
        if glas:
            b.append("  GLAS ___BLANK 1 0 %.6f %.4f 0 0 0 0 0 0" % glas)
        flag = 1 if stop else 0
        b += ['  DIAM %r %d 0 0 1 ""' % (diam, flag), '  MEMA %r %d 0 0 1 ""' % (diam, flag),
              "  POPS 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0"]
        return b

    L += block(0, 0.0, "INFINITY", 0.0)
    for i, s in enumerate(m["surfaces"]):
        last = s["thickness_mm"] is None
        glas = None
        if not last:
            nd, vd, res = model_glass(s)
            glas = (nd, vd)
            if res is not None:
                notes.append("%s: model glass nd %.6f, Vd %.3f from a Cauchy fit (largest residual %.1e)"
                             % (s["medium"], nd, vd, res))
        stop = (i + 1) == m["stop_surface"]
        diam = r_stop if stop else (12.0 if last else 5.0)
        L += block(i + 1, 1 / s["radius_mm"], 0 if last else repr(s["thickness_mm"]), diam,
                   stop=stop, coni=s["conic"], glas=glas)
    L += ["BLNK ", "TOL TOFF   0   0 0.0000000000000000E+00 0.0000000000000000E+00   0 0 0 0 0",
          "MNUM 1 1", 'MOFF   0   1 "" 0 0 0 1 1 0 0.0 "" 0']
    return "\r\n".join(L) + "\r\n", notes


# ---------------------------------------------------------------- CODE V (.seq)
def codev(m):
    waves = m["wavelengths_nm"]
    fields = fields_for(m)
    prefix = {"le-grand-relaxed": "LG", "le-grand-accommodated": "LGA", "escudero-sanz-navarro-wide-angle-eye": "ESN"}
    pre = prefix.get(m["id"], "AZ%d" % m.get("accommodation_D", 0))
    glass = {}
    for s in m["surfaces"]:
        if s["index"] and s["medium"] not in glass:
            if len(s["index"]) == 1:
                n = next(iter(s["index"].values()))
                vals = [n for _ in waves]
            else:
                vals = [s["index"]["%.1f" % w] for w in waves]
            glass[s["medium"]] = ("%s_%s" % (pre, s["medium"][:3].upper()), vals)
    out = ["! %s" % m["title"], "! Generated by EveryEyeModel scripts/make_formats.py from data/; do not edit.",
           "! Source: %s" % m["source"]]
    out += ["! " + n for n in m["notes"]]
    out += ["LEN NEW", "TITLE '%s'" % m["title"], "DIM M", "EPD %g" % EPD_MM,
            "WL " + " ".join("%g" % w for w in waves),
            "REF %d" % (waves.index(m["primary_nm"]) + 1 if m["primary_nm"] in waves else 1),
            "XAN " + " ".join("0" for _ in fields), "YAN " + " ".join(str(f) for f in fields),
            "PRV", "PWL " + " ".join("%g" % w for w in waves)]
    for name, vals in glass.values():
        out.append("'%s' " % name + " ".join("%.6f" % v for v in vals))
    out += ["END", "SO 0 1E+20"]
    for i, s in enumerate(m["surfaces"]):
        if s["thickness_mm"] is None:
            out.append("SI %r 0" % s["radius_mm"])
            continue
        out.append("S %r %r %s" % (s["radius_mm"], s["thickness_mm"], glass[s["medium"]][0]))
        if s["conic"]:
            out += ["  CON", "  K %r" % s["conic"]]
        if (i + 1) == m["stop_surface"]:
            out.append("  STO")
    out.append("GO")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- Python module
PY_HEAD = '''"""EveryEyeModel: published schematic eye models as Python data.

GENERATED by scripts/make_formats.py from data/*.csv -- do not edit by hand.
Standard library only. Lengths in millimetres; radius positive when the centre of curvature is to
the right; conic K (Q in some papers); index of the medium after the surface, keyed by wavelength
in nanometres.

    import everyeyemodel as eem
    eem.names()                       # the model ids
    m = eem.get("le-grand-relaxed")   # a dict: title, source, surfaces, stop_surface, notes
    eem.arizona(3.5)                  # the Arizona eye at any accommodation, in dioptres
    print(eem.to_csv(m, 587.6))       # a prescription table at one wavelength
"""
import copy as _copy

'''

PY_TAIL = '''

def names():
    """The ids of every model held here."""
    return list(MODELS)


def get(model_id):
    """A copy of one model, so changing it never changes the stored data."""
    return _copy.deepcopy(MODELS[model_id])


def _cauchy_from_abbe(nd, vd):
    d, f, c = 0.5876, 0.4861, 0.6563
    b = ((nd - 1) / vd) / (1 / f ** 2 - 1 / c ** 2)
    return nd - b / d ** 2, b


def arizona(A):
    """The Arizona eye at accommodation A dioptres (Schwiegerling 2004). Indices at 656.3 and
    486.1 nm come from a two-term Cauchy fit through nd and Vd, a model of the dispersion."""
    n_lens = 1.42 + 0.00256 * A - 0.00022 * A * A
    rows = [
        ("Cornea front", 7.8, -0.25, 0.55, "cornea", 1.377, 57.1),
        ("Cornea back", 6.5, -0.25, 2.97 - 0.04 * A, "aqueous", 1.337, 61.3),
        ("Lens front", 12.0 - 0.4 * A, -7.518749 + 1.285720 * A, 3.767 + 0.04 * A, "lens", n_lens, 51.9),
        ("Lens back", -5.224557 + 0.2 * A, -1.353971 - 0.431762 * A, 16.713, "vitreous", 1.336, 61.1),
        ("Retina", -13.4, 0.0, None, None, None, None),
    ]
    m = get("arizona-eye-0D")
    m.update(id="arizona-eye-%gD" % A, title="Arizona eye, %g D accommodation" % A, accommodation_D=A)
    for s, (name, R, K, t, med, nd, vd) in zip(m["surfaces"], rows):
        s.update(radius_mm=R, conic=K, thickness_mm=t)
        if nd is not None:
            a, b = _cauchy_from_abbe(nd, vd)
            s["index"] = {"%.1f" % w: a + b / (w / 1000) ** 2 for w in (656.3, 486.1)}
            s["index"]["587.6"] = nd
            s["nd"] = nd
    return m


def to_csv(m, wavelength_nm=None):
    """The prescription as CSV text at one wavelength (default: the model's primary one)."""
    w = "%.1f" % (wavelength_nm or m["primary_nm"])
    lines = ["surface,name,radius_mm,conic_K,thickness_mm,index_after_at_%snm" % w]
    for i, s in enumerate(m["surfaces"], 1):
        n = "" if not s.get("index") else s["index"].get(w, "")
        t = "" if s.get("thickness_mm") is None else s["thickness_mm"]
        r = s.get("radius_mm", "") if s.get("radius_mm") is not None else "infinity"
        lines.append("%d,%s,%s,%s,%s,%s" % (i, s["name"], r, s.get("conic", 0), t, n))
    return "\\n".join(lines) + "\\n"
'''


def python_module(ms):
    body = "MODELS = " + json.dumps({m["id"]: m for m in ms}, indent=1).replace("null", "None") \
        .replace("true", "True").replace("false", "False") + "\n"
    return PY_HEAD + body + PY_TAIL


# ---------------------------------------------------------------- write / check
def outputs():
    ms = all_models()
    files, report = {}, []
    for m in ms:
        files["formats/json/%s.json" % m["id"]] = (json.dumps(m, indent=2) + "\n").encode("utf-8")
        if m["id"] == "paraxial-reduced-eye":
            report.append((m["id"], 60.0, None))
            continue
        text, notes = zmx(m)
        files["formats/zemax/%s.zmx" % m["id"]] = text.encode("utf-16")
        files["formats/codev/%s.seq" % m["id"]] = codev(m).encode("utf-8")
        report.append((m["id"], power_D(m), 2 * stop_radius(m, EPD_MM)))
        for n in notes:
            report.append((m["id"], None, n))
    files["python/everyeyemodel.py"] = python_module(ms).encode("utf-8")
    return files, report


def main(argv):
    files, report = outputs()
    if "--check" in argv:
        stale = [p for p, b in files.items() if not (ROOT / p).exists() or (ROOT / p).read_bytes() != b]
        if stale:
            print("stale: " + ", ".join(stale))
            return 1
        print("formats: up to date (%d files)" % len(files))
        return 0
    for p, b in files.items():
        f = ROOT / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b)
    print("wrote %d files" % len(files))
    for mid, p, x in report:
        if p is not None:
            print("  %-40s power %.2f D%s" % (mid, p, "" if x is None else ", iris %.3f mm for a %g mm entrance pupil" % (x, EPD_MM)))
        else:
            print("  %-40s %s" % (mid, x))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
