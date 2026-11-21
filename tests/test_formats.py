"""Round-trip checks for the generated formats. Run: python3 -m unittest discover tests"""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_module():
    spec = importlib.util.spec_from_file_location("everyeyemodel", ROOT / "python" / "everyeyemodel.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def zmx_surfaces(path):
    """(curvature, thickness, conic, nd) for each surface after the object, from a .zmx file."""
    text = path.read_text(encoding="utf-16")
    out, cur = [], None
    for line in text.splitlines():
        t = line.split()
        if not t:
            continue
        if t[0] == "SURF":
            cur = {"curv": 0.0, "disz": None, "coni": 0.0, "nd": None, "stop": False}
            out.append(cur)
        elif cur is None:
            continue
        elif t[0] == "CURV":
            cur["curv"] = float(t[1])
        elif t[0] == "DISZ":
            cur["disz"] = None if t[1] == "INFINITY" else float(t[1])
        elif t[0] == "CONI":
            cur["coni"] = float(t[1])
        elif t[0] == "GLAS":
            cur["nd"] = float(t[4])
        elif t[0] == "STOP":
            cur["stop"] = True
    return out[1:]


def seq_surfaces(path):
    out = []
    for line in path.read_text().splitlines():
        t = line.split()
        if not t:
            continue
        if t[0] in ("S", "SI"):
            out.append({"R": float(t[1]), "t": float(t[2]), "K": 0.0, "stop": False})
        elif t[0] == "K" and out:
            out[-1]["K"] = float(t[1])
        elif t[0] == "STO" and out:
            out[-1]["stop"] = True
    return out


class Formats(unittest.TestCase):
    def setUp(self):
        self.models = {p.stem: json.loads(p.read_text()) for p in (ROOT / "formats" / "json").glob("*.json")}

    def test_up_to_date(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "make_formats.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_json_matches_csv(self):
        import csv
        rows = list(csv.DictReader(open(ROOT / "data" / "le-grand-full-theoretical-eye.csv")))
        m = self.models["le-grand-relaxed"]
        for row, s in zip(rows, m["surfaces"]):
            self.assertEqual(float(row["radius_mm"]), s["radius_mm"])
            if row["index_after"]:
                self.assertEqual(float(row["index_after"]), s["index"]["587.6"])

    def test_zemax_round_trip(self):
        for mid, m in self.models.items():
            if mid == "paraxial-reduced-eye":
                continue
            zs = zmx_surfaces(ROOT / "formats" / "zemax" / (mid + ".zmx"))
            self.assertEqual(len(zs), len(m["surfaces"]), mid)
            for i, (z, s) in enumerate(zip(zs, m["surfaces"])):
                self.assertAlmostEqual(z["curv"], 1 / s["radius_mm"], places=12, msg=mid)
                self.assertAlmostEqual(z["coni"], s["conic"], places=9, msg=mid)
                if s["thickness_mm"] is not None:
                    self.assertAlmostEqual(z["disz"], s["thickness_mm"], places=9, msg=mid)
                self.assertEqual(z["stop"], i + 1 == m["stop_surface"], mid)
            if mid.startswith("arizona"):
                self.assertAlmostEqual(zs[0]["nd"], 1.377, places=6)

    def test_codev_round_trip(self):
        for mid, m in self.models.items():
            if mid == "paraxial-reduced-eye":
                continue
            cs = seq_surfaces(ROOT / "formats" / "codev" / (mid + ".seq"))
            self.assertEqual(len(cs), len(m["surfaces"]), mid)
            for i, (c, s) in enumerate(zip(cs, m["surfaces"])):
                self.assertAlmostEqual(c["R"], s["radius_mm"], places=9, msg=mid)
                self.assertAlmostEqual(c["K"], s["conic"], places=9, msg=mid)
                self.assertEqual(c["stop"], i + 1 == m["stop_surface"], mid)

    def test_zemax_files_are_utf16_crlf(self):
        for p in (ROOT / "formats" / "zemax").glob("*.zmx"):
            b = p.read_bytes()
            self.assertEqual(b[:2], b"\xff\xfe", p.name)
            self.assertIn("\r\n", b.decode("utf-16"), p.name)

    def test_python_module(self):
        eem = load_module()
        self.assertIn("escudero-sanz-navarro-wide-angle-eye", eem.names())
        a0, stored0 = eem.arizona(0), eem.get("arizona-eye-0D")
        for s, t in zip(a0["surfaces"], stored0["surfaces"]):
            self.assertAlmostEqual(s["radius_mm"], t["radius_mm"], places=6)
        a4, stored4 = eem.arizona(4), eem.get("arizona-eye-4D")
        for s, t in zip(a4["surfaces"], stored4["surfaces"]):
            self.assertAlmostEqual(s["radius_mm"], t["radius_mm"], places=6)
            self.assertAlmostEqual(s["conic"], t["conic"], places=6)
        # the axial length does not change with accommodation
        L = lambda m: sum(s["thickness_mm"] for s in m["surfaces"] if s["thickness_mm"] is not None)
        self.assertAlmostEqual(L(eem.arizona(0)), L(eem.arizona(5.5)), places=9)
        self.assertTrue(eem.to_csv(eem.get("le-grand-relaxed")).startswith("surface,name"))
        # get returns a copy
        m = eem.get("le-grand-relaxed")
        m["surfaces"][0]["radius_mm"] = 0
        self.assertEqual(eem.get("le-grand-relaxed")["surfaces"][0]["radius_mm"], 7.8)


if __name__ == "__main__":
    unittest.main()
