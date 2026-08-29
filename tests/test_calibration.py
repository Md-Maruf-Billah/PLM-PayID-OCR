import json

import pytest

import calibration


@pytest.fixture
def local_config_path(tmp_path, monkeypatch):
    path = tmp_path / "local.json"
    monkeypatch.setattr(calibration, "LOCAL_CONFIG_PATH", path)
    return path


class TestSaveRegions:
    def test_writes_regions_to_fresh_file(self, local_config_path):
        calibration.save_regions(
            {"primary": [0.1, 0.1, 0.5, 0.2], "secondary": [0.1, 0.6, 0.5, 0.2]}
        )

        saved = json.loads(local_config_path.read_text())
        assert saved["regions"]["primary"]["roi"] == [0.1, 0.1, 0.5, 0.2]
        assert saved["regions"]["secondary"]["roi"] == [0.1, 0.6, 0.5, 0.2]

    def test_preserves_other_existing_keys(self, local_config_path):
        local_config_path.write_text(json.dumps({"camera": {"device_index": 2}}))

        calibration.save_regions({"primary": [0, 0, 1, 1], "secondary": [0, 0, 1, 1]})

        saved = json.loads(local_config_path.read_text())
        assert saved["camera"]["device_index"] == 2
        assert "regions" in saved

    def test_overwrites_previous_regions(self, local_config_path):
        calibration.save_regions({"primary": [0, 0, 1, 1], "secondary": [0, 0, 1, 1]})
        calibration.save_regions(
            {"primary": [0.2, 0.2, 0.3, 0.3], "secondary": [0.4, 0.4, 0.3, 0.3]}
        )

        saved = json.loads(local_config_path.read_text())
        assert saved["regions"]["primary"]["roi"] == [0.2, 0.2, 0.3, 0.3]

    def test_recovers_from_corrupted_existing_file(self, local_config_path):
        local_config_path.write_text("{not valid json")

        calibration.save_regions({"primary": [0, 0, 1, 1], "secondary": [0, 0, 1, 1]})

        saved = json.loads(local_config_path.read_text())
        assert saved["regions"]["primary"]["roi"] == [0, 0, 1, 1]

    def test_no_leftover_temp_file(self, local_config_path):
        calibration.save_regions({"primary": [0, 0, 1, 1], "secondary": [0, 0, 1, 1]})

        leftovers = list(local_config_path.parent.glob("*.tmp"))
        assert leftovers == []


class TestCalibrationExists:
    def test_false_when_missing(self, local_config_path):
        assert calibration.calibration_exists() is False

    def test_true_when_present(self, local_config_path):
        local_config_path.write_text("{}")
        assert calibration.calibration_exists() is True
