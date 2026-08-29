from code_detector import Confidence, extract_all_codes, extract_code, resolve_code


class TestExtractCode:
    def test_clean_match(self):
        assert extract_code("YABORKFH") == "YABORKFH"

    def test_strips_whitespace_and_newlines(self):
        assert extract_code("  YABORKFH\n\n") == "YABORKFH"

    def test_wrong_length_rejected(self):
        assert extract_code("YABORKF") is None
        assert extract_code("YABORKFHX") is None

    def test_digit_rejected(self):
        assert extract_code("YAB0RKFH") is None

    def test_empty_input(self):
        assert extract_code("") is None


class TestExtractAllCodes:
    def test_finds_codes_across_lines(self):
        text = "PLAYLIVE MELBOURNE\nYABORKFH\nHOW TO DEPOSIT\nYABORKFH\nHAND THIS SLIP TO CASHIER"
        assert extract_all_codes(text) == ["YABORKFH", "YABORKFH"]

    def test_ignores_non_matching_lines(self):
        text = "PLAYLIVE MELBOURNE\nSEND FUNDS USING CODE\n"
        assert extract_all_codes(text) == []


class TestResolveCode:
    def test_primary_and_secondary_match(self):
        result = resolve_code("YABORKFH", "YABORKFH", [])
        assert result.code == "YABORKFH"
        assert result.confidence == Confidence.VERY_HIGH

    def test_primary_and_secondary_disagree_rejects(self):
        result = resolve_code("YABORKFH", "YABDRKFH", [])
        assert result.code is None
        assert result.confidence == Confidence.NONE

    def test_primary_only_confirmed_by_full_slip(self):
        result = resolve_code("YABORKFH", None, ["YABORKFH", "YABORKFH"])
        assert result.code == "YABORKFH"
        assert result.confidence == Confidence.HIGH

    def test_secondary_only_confirmed_by_full_slip(self):
        result = resolve_code(None, "YABORKFH", ["YABORKFH"])
        assert result.code == "YABORKFH"
        assert result.confidence == Confidence.HIGH

    def test_primary_only_no_full_slip_signal(self):
        result = resolve_code("YABORKFH", None, [])
        assert result.code == "YABORKFH"
        assert result.confidence == Confidence.MEDIUM

    def test_primary_conflicts_with_full_slip_rejects(self):
        result = resolve_code("YABORKFH", None, ["MBTIVXOT"])
        assert result.code is None
        assert result.confidence == Confidence.NONE

    def test_full_slip_only_recovers_code(self):
        result = resolve_code(None, None, ["YABORKFH", "YABORKFH"])
        assert result.code == "YABORKFH"
        assert result.confidence == Confidence.MEDIUM

    def test_full_slip_only_conflicting_codes_rejects(self):
        result = resolve_code(None, None, ["YABORKFH", "MBTIVXOT"])
        assert result.code is None
        assert result.confidence == Confidence.NONE

    def test_nothing_detected(self):
        result = resolve_code(None, None, [])
        assert result.code is None
        assert result.confidence == Confidence.NONE
