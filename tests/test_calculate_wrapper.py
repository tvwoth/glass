"""
Tests for app.core.calculate function wrapper.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.core.calculate import calculate


CONFIG_PREMIER = {
    "j_x": -48,
    "c_x": -160,
    "cd_len": 65,
    "de_len": 20,
    "fg_len": 20,
    "gh_len": 70,
    "hi_len": 43.5,
    "jk_len": 8.5,
    "hcor": 80,
    "rev": False,
}


class TestCalculateWrapper:
    """Tests for the calculate function wrapper."""

    def test_basic_calculation(self):
        """Basic calculation with n1=100, n2=50, n4=None, angle_EF=5."""
        result = calculate(
            input_data={"n1": 100, "n2": 50, "n4": None, "angle_EF": 5},
            config=CONFIG_PREMIER,
        )
        assert result["n1"] == 100
        assert result["n2"] == 50
        assert result["n4"] is not None
        assert result["n4"] > 0
        assert result["angle_EF"] == 5
        assert result["angle_D"] == 185
        assert result["alpha"] == 85
        assert result["n3"] is not None
        assert len(result["points"]) == 11

    def test_n1_missing(self):
        """Calculate with n1=None."""
        result = calculate(
            input_data={"n1": None, "n2": 50, "n4": 120, "angle_EF": 5},
            config=CONFIG_PREMIER,
        )
        assert result["n1"] is not None
        assert result["n1"] > 0
        assert result["n4"] == 200  # 120 + 80 HCOR

    def test_n4_missing(self):
        """Calculate with n4=None."""
        result = calculate(
            input_data={"n1": 100, "n2": 50, "n4": None, "angle_EF": 5},
            config=CONFIG_PREMIER,
        )
        assert result["n4"] is not None
        assert result["n4"] > 0

    def test_error_on_four_params(self):
        """All 4 params given should raise ValueError."""
        with pytest.raises(ValueError):
            calculate(
                input_data={"n1": 100, "n2": 50, "n4": 120, "angle_EF": 5},
                config=CONFIG_PREMIER,
            )

    def test_returns_n3(self):
        """Result should contain n3 which is n4 - hcor."""
        result = calculate(
            input_data={"n1": 100, "n2": 50, "n4": None, "angle_EF": 5},
            config=CONFIG_PREMIER,
        )
        assert "n3" in result
        assert result["n3"] == result["n4"] - CONFIG_PREMIER["hcor"]

    def test_rev_config(self):
        """REV flag in config should be respected."""
        config_rev = dict(CONFIG_PREMIER)
        config_rev["rev"] = True
        result = calculate(
            input_data={"n1": 100, "n2": 50, "n4": None, "angle_EF": 5},
            config=config_rev,
        )
        # With REV=True, D point should be c_y + CD_LEN = -100 + 65 = -35
        d_point = result["points"][3]
        assert d_point[1] == -35

    def test_sindikat_config(self):
        """Test with Синдикат config."""
        config_sindikat = {
            "j_x": -40,
            "c_x": -140,
            "cd_len": 55,
            "de_len": 18,
            "fg_len": 18,
            "gh_len": 60,
            "hi_len": 38,
            "jk_len": 7.5,
            "hcor": 70,
            "rev": False,
        }
        result = calculate(
            input_data={"n1": None, "n2": 50, "n4": 100, "angle_EF": 5},
            config=config_sindikat,
        )
        assert result["n1"] is not None
        assert result["n1"] > 0
        assert result["n4"] == 170  # 100 + 70 HCOR