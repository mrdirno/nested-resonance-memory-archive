"""Archive boundary and non-destructive cleanup tests.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0-only
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


audit = module("archive_audit", "tools/archive/audit.py")
cleanup = module("archive_cleanup", "automation/scripts/cleanup_repo.py")


class ArchiveBoundaryTests(unittest.TestCase):
    def test_slicer_profile_requires_content_not_a_generic_config_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "project_settings.config"
            # Minimal test-only signature; no real machine configuration values.
            profile = {key: None for key in ("nozzle_diameter", "printer_model",
                       "printer_settings_id", "layer_height")}
            path.write_text(json.dumps(profile))
            self.assertTrue(audit.private_artifact(path.name, root))
            (root / "renamed.json").write_bytes(path.read_bytes())
            self.assertTrue(audit.private_artifact("renamed.json", root))
            path.write_text(json.dumps({"name": "application", "layer_height": 1,
                                        "display": {"theme": "dark"}}))
            self.assertFalse(audit.private_artifact(path.name, root))
            path.write_text("[display]\ntheme=dark\n")
            self.assertFalse(audit.private_artifact(path.name, root))

    def test_unpacked_3mf_package_identified_by_xml_even_without_geometry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "export"
            (package / "3D").mkdir(parents=True)
            (package / "Metadata").mkdir()
            types = package / "[Content_Types].xml"
            model = package / "3D/3dmodel.model"
            preview = package / "Metadata/preview.png"
            types.write_text('<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
            model.write_text('<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources/><build/></model>')
            preview.write_bytes(b"test preview")
            for file in (types, model, preview):
                self.assertTrue(audit.private_artifact(file.relative_to(root).as_posix(), root))
            # Lookalike directory names and generic XML alone are insufficient.
            model.write_text('<model><resources/></model>')
            for file in (types, model, preview):
                self.assertFalse(audit.private_artifact(file.relative_to(root).as_posix(), root))

    def test_proprietary_paths_are_rejected_case_insensitively(self):
        for path in ("fabrication/scripts/x.py", "data/model.OBJ", "a/job.gcode", "x/slicer_profiles/a.json", "x/printer_configs/a.ini", "x/workspace/cache/a.txt"):
            with self.subTest(path=path):
                self.assertTrue(audit.private_artifact(path))
        for path in ("docs/protocols/FABRICATION_PROTOCOL.md", "src/printer_interface.py", "data/results/halo.json"):
            self.assertFalse(audit.private_artifact(path))

    def test_registry_requires_real_entry_points(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "real.py").write_text("print(1)\n")
            registry = {"schema_version": 1, "components": [{"id": "test", "status": "experimental", "summary": "Measured source", "next_action": "Run the source", "paths": ["real.py"], "entry_points": ["missing.py"], "evidence": ["real.py"]}]}
            self.assertIn("missing entry_points: missing.py", "\n".join(audit.validate_registry(root, registry)))
            registry["components"][0]["entry_points"] = ["real.py"]
            self.assertEqual([], audit.validate_registry(root, registry))
            registry["components"][0]["status"] = "production-certified"
            self.assertTrue(audit.validate_registry(root, registry))

    def test_stp_exception_requires_actual_signaltap_xml_inside_fpga(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "fpga").mkdir()
            path = root / "fpga/session.stp"
            path.write_text('<session><instance source_file="sld_signaltap.vhd"><node_ip_info/></instance></session>')
            self.assertFalse(audit.private_artifact("fpga/session.stp", root))
            (root / "design.stp").write_bytes(path.read_bytes())
            self.assertTrue(audit.private_artifact("design.stp", root))
            path.write_text('ISO-10303-21; HEADER; FILE_DESCRIPTION(("design"));')
            self.assertTrue(audit.private_artifact("fpga/session.stp", root))
            path.write_text('<session/>')
            self.assertTrue(audit.private_artifact("fpga/session.stp", root))

    def test_rejects_path_traversal_and_escaping_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "escape").symlink_to(root.parent, target_is_directory=True)
            for path in ("../outside", "/etc/passwd", "escape/outside", "..\\outside"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    audit.local_path(root, path)

    def test_inventory_uses_real_git_index_excludes_untracked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "measured.txt").write_text("real filesystem evidence\n")
            subprocess.run(["git", "-C", str(root), "add", "measured.txt"], check=True)
            (root / "untracked.txt").write_text("private work in progress\n")
            self.assertEqual(["measured.txt"], audit.tracked_files(root))


class CleanupTests(unittest.TestCase):
    def test_preview_creates_nothing_and_explicit_apply_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "temp_measurement.log"
            source.write_bytes(b"unaltered evidence\x00\xff")
            moves = cleanup.plan_moves(root)
            self.assertEqual(1, len(moves))
            self.assertTrue(source.exists())
            self.assertFalse((root / "data").exists())
            cleanup.apply_move(moves[0])
            self.assertFalse(source.exists())
            self.assertEqual(b"unaltered evidence\x00\xff", moves[0].target.read_bytes())

    def test_collision_at_apply_does_not_overwrite_or_remove_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "temp_test.log"
            source.write_text("source")
            move = cleanup.plan_moves(root)[0]
            move.target.parent.mkdir(parents=True)
            move.target.write_text("history")
            with self.assertRaises(FileExistsError):
                cleanup.apply_move(move)
            self.assertEqual("source", source.read_text())
            self.assertEqual("history", move.target.read_text())

    def test_escaping_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "temp_run.log").write_text("retain")
            (root / "data").symlink_to(root.parent, target_is_directory=True)
            with self.assertRaises(ValueError):
                cleanup.plan_moves(root)
            self.assertTrue((root / "temp_run.log").exists())

    def test_symlink_sources_and_dangling_destinations_are_not_moved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "temp_symlink.log").symlink_to(root / "missing")
            (root / "temp_collision.log").write_text("retain")
            target = root / "data/temp"
            target.mkdir(parents=True)
            (target / "temp_collision.log").symlink_to(root / "missing")
            self.assertEqual([], cleanup.plan_moves(root))
            self.assertTrue((root / "temp_collision.log").exists())

    def test_apply_requires_explicit_reviewed_names(self):
        with self.assertRaises(SystemExit) as result:
            cleanup.main(["--apply"])
        self.assertEqual(2, result.exception.code)

    def test_invalid_root_is_read_only_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "temp_test.log").write_text("retain")
            self.assertEqual(1, cleanup.main(["--root", directory]))
            self.assertEqual(["temp_test.log"], [p.name for p in root.iterdir()])


if __name__ == "__main__":
    unittest.main()
