"""
Comprehensive tests for ContourCalculator.
These tests capture the EXACT behavior of app/calculator/contour_calculator.py
before any refactoring. They serve as the reference test suite.

IMPORTANT: These tests MUST pass against the original calculator.
Any migration to app/core/ must produce identical results.
"""
import sys
import os
import math
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.calculator.contour_calculator import ContourCalculator


CONFIG_PREMIER = {
    "j_x": -48, "c_x": -160, "cd_len": 65, "de_len": 20,
    "fg_len": 20, "gh_len": 70, "hi_len": 43.5, "jk_len": 8.5, "hcor": 80,
}

CONFIG_SINDIKAT = {
    "j_x": -40, "c_x": -140, "cd_len": 55, "de_len": 18,
    "fg_len": 18, "gh_len": 60, "hi_len": 38, "jk_len": 7.5, "hcor": 70,
}

CONFIG_DEFAULT = {
    "j_x": 0, "c_x": 0, "cd_len": 0, "de_len": 0,
    "fg_len": 0, "gh_len": 0, "hi_len": 0, "jk_len": 0, "hcor": 0,
}


def apply_config(calc, config):
    calc.set_j_x(config["j_x"])
    calc.set_c_x(config["c_x"])
    calc.set_cd_len(config["cd_len"])
    calc.set_de_len(config["de_len"])
    calc.set_fg_len(config["fg_len"])
    calc.set_gh_len(config["gh_len"])
    calc.set_hi_len(config["hi_len"])
    calc.set_jk_len(config["jk_len"])
    calc.set_hcor(config["hcor"])


class TestContourCalculatorPremier:
    """Tests using Премьер комплект configuration."""

    def setup_method(self):
        self.calc = ContourCalculator()
        apply_config(self.calc, CONFIG_PREMIER)

    def test_state_after_config(self):
        assert self.calc.J_X == -48
        assert self.calc.K_X == -48
        assert self.calc.C_X == -160
        assert self.calc.D_X == -160
        assert self.calc.CD_LEN == 65
        assert self.calc.DE_LEN == 20
        assert self.calc.FG_LEN == 20
        assert self.calc.GH_LEN == 70
        assert self.calc.HI_LEN == 43.5
        assert self.calc.JK_LEN == 8.5
        assert self.calc.HCOR == 80

    def test_calculate_n1_missing(self):
        """n1=None, n2=50, n4=120, angle_EF=5 -> stored n4=200 (120+80)"""
        self.calc.set_directions(REV=False)
        points = self.calc.calculate(n1=None, n2=50, n4=120, angle_EF=5)
        assert self.calc.n1 is not None and self.calc.n1 > 0
        assert self.calc.n2 == 50
        # n4 stored as input + HCOR = 120 + 80 = 200
        assert self.calc.n4 == 200
        assert self.calc.angle_EF == 5
        assert self.calc.angle_D == 185
        # n3 = n4 - HCOR = 200 - 80 = 120
        assert self.calc.get_n3() == 120
        assert len(points) == 11
        assert points[0] == (0, 0)
        assert points[10][0] == -48
        assert points[10][1] == 0

    def test_calculate_n2_missing(self):
        """n1=100, n2=None, n4=120, angle_EF=5 -> stored n4=200"""
        self.calc.set_directions(REV=False)
        points = self.calc.calculate(n1=100, n2=None, n4=120, angle_EF=5)
        assert self.calc.n1 == 100
        assert self.calc.n2 is not None and self.calc.n2 > 0
        assert self.calc.n4 == 200
        assert self.calc.angle_EF == 5
        assert self.calc.angle_D == 185
        assert len(points) == 11

    def test_calculate_n4_missing(self):
        """n1=100, n2=50, n4=None, angle_EF=5 -> n4 calculated (no HCOR since None)"""
        self.calc.set_directions(REV=False)
        points = self.calc.calculate(n1=100, n2=50, n4=None, angle_EF=5)
        assert self.calc.n1 == 100
        assert self.calc.n2 == 50
        assert self.calc.n4 is not None and self.calc.n4 > 0
        assert self.calc.angle_EF == 5
        assert self.calc.angle_D == 185
        assert len(points) == 11

    def test_calculate_angle_missing(self):
        """
        n1=100, n2=50, n4=69.17, angle_EF=None
        stored_n4 = 69.17 + 80 = 149.17 (geometric distance from Test 1)
        Solver should find angle_EF ≈ 5
        """
        self.calc.set_directions(REV=False)
        # n3 input = geometric_n4 - HCOR = 149.17 - 80 = 69.17
        points = self.calc.calculate(n1=100, n2=50, n4=69.17, angle_EF=None)
        assert self.calc.n1 == 100
        assert self.calc.n2 == 50
        assert self.calc.angle_EF is not None
        assert self.calc.angle_D is not None
        # Should be close to 5 (original angle_EF used)
        assert abs(self.calc.angle_EF - 5) < 0.5, f"angle_EF={self.calc.angle_EF}, expected ~5"
        assert self.calc.angle_D == 180 + self.calc.angle_EF
        assert len(points) == 11

    def test_four_params_error(self):
        """4 params given -> ValueError."""
        with pytest.raises(ValueError) as ctx:
            self.calc.calculate(n1=100, n2=50, n4=120, angle_EF=5)
        assert "три" in str(ctx.value)

    def test_two_params_error(self):
        """2 params given -> ValueError."""
        with pytest.raises(ValueError) as ctx:
            self.calc.calculate(n1=100, n2=None, n4=None, angle_EF=5)
        assert "три" in str(ctx.value)

    def test_angle_ef_out_of_range(self):
        """angle_EF=15 (3 params) -> range error."""
        with pytest.raises(ValueError) as ctx:
            self.calc.calculate(n1=100, n2=50, n4=None, angle_EF=15)
        assert "диапазоне" in str(ctx.value) or "0°" in str(ctx.value)

    def test_negative_n1_error(self):
        """n1=-10 -> param validation error."""
        with pytest.raises(ValueError) as ctx:
            self.calc.calculate(n1=-10, n2=50, n4=120, angle_EF=None)
        assert "положительной" in str(ctx.value)

    def test_zero_config_error(self):
        """All-zero config -> error."""
        calc2 = ContourCalculator()
        apply_config(calc2, CONFIG_DEFAULT)
        with pytest.raises(ValueError) as ctx:
            calc2.calculate(n1=100, n2=50, n4=None, angle_EF=5)
        assert "Выберите конфигурацию" in str(ctx.value)

    def test_point_positions(self):
        self.calc.set_directions(REV=False)
        points = self.calc.calculate(n1=100, n2=50, n4=None, angle_EF=5)
        assert points[0] == (0, 0)
        assert points[1] == (0, -100)
        assert points[2] == (-160, -100)
        assert points[3] == (-160, -165)
        assert points[10][0] == -48
        assert points[10][1] == 0
        assert points[9][0] == -48
        assert points[9][1] == -8.5

    def test_rev_flag(self):
        self.calc.set_directions(REV=True)
        points = self.calc.calculate(n1=100, n2=50, n4=None, angle_EF=5)
        assert self.calc.REV is True
        assert points[3][1] == -35  # c_y + CD_LEN
        assert len(points) == 11

    def test_alpha_calculation(self):
        self.calc.set_directions(REV=False)
        self.calc.calculate(n1=100, n2=50, n4=None, angle_EF=5)
        assert self.calc.alpha == 85
        assert self.calc.alpha == 270 - self.calc.angle_D

    def test_angle_ef_zero(self):
        self.calc.set_directions(REV=False)
        points = self.calc.calculate(n1=100, n2=50, n4=None, angle_EF=0)
        assert self.calc.angle_EF == 0
        assert self.calc.angle_D == 180

    def test_angle_ef_ten(self):
        self.calc.set_directions(REV=False)
        points = self.calc.calculate(n1=100, n2=50, n4=None, angle_EF=10)
        assert self.calc.angle_EF == 10
        assert self.calc.angle_D == 190


class TestContourCalculatorSindikat:
    def setup_method(self):
        self.calc = ContourCalculator()
        apply_config(self.calc, CONFIG_SINDIKAT)

    def test_n1_missing(self):
        self.calc.set_directions(REV=False)
        points = self.calc.calculate(n1=None, n2=50, n4=100, angle_EF=5)
        assert self.calc.n1 is not None and self.calc.n1 > 0
        assert self.calc.n2 == 50
        assert self.calc.n4 == 170  # 100 + 70 HCOR
        assert self.calc.angle_EF == 5

    def test_n2_missing(self):
        self.calc.set_directions(REV=False)
        points = self.calc.calculate(n1=80, n2=None, n4=100, angle_EF=5)
        assert self.calc.n1 == 80
        assert self.calc.n2 is not None and self.calc.n2 > 0

    def test_n4_missing(self):
        self.calc.set_directions(REV=False)
        points = self.calc.calculate(n1=80, n2=50, n4=None, angle_EF=5)
        assert self.calc.n1 == 80
        assert self.calc.n2 == 50
        assert self.calc.n4 is not None and self.calc.n4 > 0


class TestContourCalculatorIndividualMethods:
    """Test individual point calculation methods."""

    def setup_method(self):
        self.calc = ContourCalculator()
        apply_config(self.calc, CONFIG_PREMIER)
        self.calc.n1 = 100
        self.calc.n2 = 50
        self.calc.REV = False

    def test_a(self):
        assert self.calc.calculate_a() == (0, 0)
    def test_b(self):
        assert self.calc.calculate_b() == (0, -100)
    def test_c(self):
        assert self.calc.calculate_c() == (-160, -100)
    def test_d_non_rev(self):
        assert self.calc.calculate_d(-100) == (-160, -165)
    def test_d_rev(self):
        self.calc.REV = True
        assert self.calc.calculate_d(-100) == (-160, -35)
    def test_e_non_rev(self):
        ar = math.radians(85)
        e = self.calc.calculate_e(-160, -165, ar)
        assert abs(e[0] - (-160 + 20 * math.cos(ar))) < 1e-10
        assert abs(e[1] - (-165 - 20 * math.sin(ar))) < 1e-10
    def test_e_rev(self):
        self.calc.REV = True
        ar = math.radians(85)
        e = self.calc.calculate_e(-160, -35, ar)
        assert abs(e[0] - (-160 - 20 * math.cos(ar))) < 1e-10
        assert abs(e[1] - (-35 + 20 * math.sin(ar))) < 1e-10
    def test_f(self):
        ar = math.radians(85)
        e = (-158.26, -184.92)
        f = self.calc.calculate_f(e[0], e[1], ar)
        expected_fx = e[0] + 50 * math.cos(ar + math.pi/2)
        expected_fy = e[1] - 50 * math.sin(ar + math.pi/2)
        assert abs(f[0] - expected_fx) < 1e-10
        assert abs(f[1] - expected_fy) < 1e-10
    def test_g(self):
        ar = math.radians(85)
        f = (-158.26, -134.92)
        g = self.calc.calculate_g(f[0], f[1], ar)
        assert abs(g[0] - (-158.26 - 20 * math.cos(ar))) < 1e-10
        assert abs(g[1] - (-134.92 + 20 * math.sin(ar))) < 1e-10
    def test_h(self):
        assert self.calc.calculate_h(-160, -115) == (-160, -45)
    def test_i(self):
        assert self.calc.calculate_i(-160, -115) == (-116.5, -45)
    def test_j(self):
        assert self.calc.calculate_j() == (-48, -8.5)
    def test_k(self):
        assert self.calc.calculate_k() == (-48, 0)