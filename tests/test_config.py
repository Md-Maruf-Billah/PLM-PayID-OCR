import json

import config


def _write_default(tmp_path):
    default_path = tmp_path / "config.json"
    default_path.write_text(json.dumps({"camera": {"device_index": 0}, "ocr": {"lang": "eng"}}))
    return default_path


class TestLoadConfig:
    def test_no_local_override_returns_defaults(self, tmp_path):
        default_path = _write_default(tmp_path)
        local_path = tmp_path / "local.json"

        result = config.load_config(default_path=default_path, local_path=local_path)

        assert result["camera"]["device_index"] == 0

    def test_local_override_deep_merges(self, tmp_path):
        default_path = _write_default(tmp_path)
        local_path = tmp_path / "local.json"
        local_path.write_text(json.dumps({"camera": {"device_index": 2}}))

        result = config.load_config(default_path=default_path, local_path=local_path)

        assert result["camera"]["device_index"] == 2
        assert result["ocr"]["lang"] == "eng"  # untouched default preserved

    def test_corrupted_local_falls_back_to_defaults(self, tmp_path, capsys):
        default_path = _write_default(tmp_path)
        local_path = tmp_path / "local.json"
        local_path.write_text("{not valid json")

        result = config.load_config(default_path=default_path, local_path=local_path)

        assert result["camera"]["device_index"] == 0
        assert "WARNING" in capsys.readouterr().err

    def test_local_json_not_an_object_falls_back_to_defaults(self, tmp_path, capsys):
        default_path = _write_default(tmp_path)
        local_path = tmp_path / "local.json"
        local_path.write_text(json.dumps(["not", "a", "dict"]))

        result = config.load_config(default_path=default_path, local_path=local_path)

        assert result["camera"]["device_index"] == 0
        assert "WARNING" in capsys.readouterr().err
