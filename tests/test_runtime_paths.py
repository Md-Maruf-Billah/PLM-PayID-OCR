import sys
from pathlib import Path

import runtime_paths


class TestIsFrozen:
    def test_false_by_default(self, monkeypatch):
        monkeypatch.delattr(sys, "frozen", raising=False)
        assert runtime_paths.is_frozen() is False

    def test_true_when_frozen_attr_set(self, monkeypatch):
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        assert runtime_paths.is_frozen() is True


class TestBundleRoot:
    def test_dev_mode_is_project_root(self, monkeypatch):
        monkeypatch.delattr(sys, "frozen", raising=False)
        root = runtime_paths.bundle_root()
        assert (root / "src").is_dir()
        assert (root / "config" / "config.json").exists()

    def test_frozen_mode_uses_meipass(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
        assert runtime_paths.bundle_root() == tmp_path


class TestUserDataDir:
    def test_lives_under_home_application_support(self, monkeypatch, tmp_path):
        monkeypatch.setenv("HOME", str(tmp_path))
        path = runtime_paths.user_data_dir()
        assert path == tmp_path / "Library" / "Application Support" / runtime_paths.APP_NAME
        assert path.is_dir()


class TestBundledTesseract:
    def test_none_when_not_frozen(self, monkeypatch):
        monkeypatch.delattr(sys, "frozen", raising=False)
        assert runtime_paths.bundled_tesseract_cmd() is None
        assert runtime_paths.bundled_tessdata_dir() is None

    def test_none_when_frozen_but_missing(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
        assert runtime_paths.bundled_tesseract_cmd() is None
        assert runtime_paths.bundled_tessdata_dir() is None

    def test_found_when_frozen_and_present(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

        tess_bin_dir = tmp_path / "tesseract-bin"
        tess_bin_dir.mkdir()
        (tess_bin_dir / "tesseract").write_text("")
        tessdata_dir = tmp_path / "tessdata"
        tessdata_dir.mkdir()

        assert runtime_paths.bundled_tesseract_cmd() == str(tess_bin_dir / "tesseract")
        assert runtime_paths.bundled_tessdata_dir() == str(tessdata_dir)
