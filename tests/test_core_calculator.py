"""
Verification test: app.core.calculator MUST produce IDENTICAL results
to app.calculator.contour_calculator for ALL inputs.
"""
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from app.legacy.contour_calculator import ContourCalculator as OriginalCalculator
from app.core.calculator import ContourCalculator as NewCalculator


CONFIG_PREMIER = {
    "j_x": -48, "c_x": -160, "cd_len": 65, "de_len": 20,
    "fg_len": 20, "gh_len": 70, "hi_len": 43.5, "jk_len": 8.5, "hcor": 80,
}

CONFIG_SINDIKAT = {
    "j_x": -40, "c_x": -140, "cd_len": 55, "de_len": 18,
    "fg_len": 18, "gh_len": 60, "hi_len": 38, "jk_len": 7.5, "hcor": 70,
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


def assert_calculators_equal(orig, new, test_name, check_n4_with_hcor=True):
    """Assert that original and new calculators produce identical results."""
    # Check calculated values
    assert orig.n1 == pytest.approx(new.n1, abs=1e-10), f"{test_name}: n1 mismatch: {orig.n1} vs {new.n1}"
    assert orig.n2 == pytest.approx(new.n2, abs=1e-10), f"{test_name}: n2 mismatch: {orig.n2} vs {new.n2}"
    assert orig.n4 == pytest.approx(new.n4, abs=1e-10), f"{test_name}: n4 mismatch: {orig.n4} vs {new.n4}"
    assert orig.angle_EF == pytest.approx(new.angle_EF, abs=1e-10), f"{test_name}: angle_EF mismatch"
    assert orig.angle_D == pytest.approx(new.angle_D, abs=1e-10), f"{test_name}: angle_D mismatch"
    assert orig.alpha == pytest.approx(new.alpha, abs=1e-10), f"{test_name}: alpha mismatch"
    assert orig.REV == new.REV, f"{test_name}: REV mismatch"
    
    # Check points
    assert len(orig_points := orig.calculate_points()) == len(new_points := new.calculate_points()), \
        f"{test_name}: point count mismatch"
    
    for i, (o_pt, n_pt) in enumerate(zip(orig_points, new_points)):
        assert o_pt[0] == pytest.approx(n_pt[0], abs=1e-10), \
            f"{test_name}: point {i} x mismatch: {o_pt[0]} vs {n_pt[0]}"
        assert o_pt[1] == pytest.approx(n_pt[1], abs=1e-10), \
            f"{test_name}: point {i} y mismatch: {o_pt[1]} vs {n_pt[1]}"
    
    # Check getter methods
    assert orig.get_n3() == pytest.approx(new.get_n3(), abs=1e-10), f"{test_name}: n3 mismatch"
    assert orig.get_angle_EF() == pytest.approx(new.get_angle_EF(), abs=1e-10), f"{test_name}: get_angle_EF mismatch"


class TestCalculatorEquivalence:
    """Verify that new core calculator is identical to the original."""

    def test_n1_missing_premier(self):
        """n1=None, n2=50, n4=120, angle_EF=5"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_PREMIER)
        apply_config(new, CONFIG_PREMIER)
        orig.set_directions(REV=False)
        new.set_directions(REV=False)
        
        o_pts = orig.calculate(n1=None, n2=50, n4=120, angle_EF=5)
        n_pts = new.calculate(n1=None, n2=50, n4=120, angle_EF=5)
        
        assert_calculators_equal(orig, new, "n1_missing_premier")

    def test_n2_missing_premier(self):
        """n1=100, n2=None, n4=120, angle_EF=5"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_PREMIER)
        apply_config(new, CONFIG_PREMIER)
        orig.set_directions(REV=False)
        new.set_directions(REV=False)
        
        o_pts = orig.calculate(n1=100, n2=None, n4=120, angle_EF=5)
        n_pts = new.calculate(n1=100, n2=None, n4=120, angle_EF=5)
        
        assert_calculators_equal(orig, new, "n2_missing_premier")

    def test_n4_missing_premier(self):
        """n1=100, n2=50, n4=None, angle_EF=5"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_PREMIER)
        apply_config(new, CONFIG_PREMIER)
        orig.set_directions(REV=False)
        new.set_directions(REV=False)
        
        o_pts = orig.calculate(n1=100, n2=50, n4=None, angle_EF=5)
        n_pts = new.calculate(n1=100, n2=50, n4=None, angle_EF=5)
        
        assert_calculators_equal(orig, new, "n4_missing_premier")

    def test_n1_missing_sindikat(self):
        """n1=None, n2=50, n4=100, angle_EF=5"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_SINDIKAT)
        apply_config(new, CONFIG_SINDIKAT)
        orig.set_directions(REV=False)
        new.set_directions(REV=False)
        
        o_pts = orig.calculate(n1=None, n2=50, n4=100, angle_EF=5)
        n_pts = new.calculate(n1=None, n2=50, n4=100, angle_EF=5)
        
        assert_calculators_equal(orig, new, "n1_missing_sindikat")

    def test_n2_missing_sindikat(self):
        """n1=80, n2=None, n4=100, angle_EF=5"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_SINDIKAT)
        apply_config(new, CONFIG_SINDIKAT)
        orig.set_directions(REV=False)
        new.set_directions(REV=False)
        
        o_pts = orig.calculate(n1=80, n2=None, n4=100, angle_EF=5)
        n_pts = new.calculate(n1=80, n2=None, n4=100, angle_EF=5)
        
        assert_calculators_equal(orig, new, "n2_missing_sindikat")

    def test_n4_missing_sindikat(self):
        """n1=80, n2=50, n4=None, angle_EF=5"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_SINDIKAT)
        apply_config(new, CONFIG_SINDIKAT)
        orig.set_directions(REV=False)
        new.set_directions(REV=False)
        
        o_pts = orig.calculate(n1=80, n2=50, n4=None, angle_EF=5)
        n_pts = new.calculate(n1=80, n2=50, n4=None, angle_EF=5)
        
        assert_calculators_equal(orig, new, "n4_missing_sindikat")
    
    def test_rev_flag_true_premier(self):
        """REV=True with n1=100, n2=50, n4=None, angle_EF=5"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_PREMIER)
        apply_config(new, CONFIG_PREMIER)
        orig.set_directions(REV=True)
        new.set_directions(REV=True)
        
        o_pts = orig.calculate(n1=100, n2=50, n4=None, angle_EF=5)
        n_pts = new.calculate(n1=100, n2=50, n4=None, angle_EF=5)
        
        assert_calculators_equal(orig, new, "rev_true_premier")
    
    def test_angle_ef_zero(self):
        """angle_EF=0"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_PREMIER)
        apply_config(new, CONFIG_PREMIER)
        orig.set_directions(REV=False)
        new.set_directions(REV=False)
        
        o_pts = orig.calculate(n1=100, n2=50, n4=None, angle_EF=0)
        n_pts = new.calculate(n1=100, n2=50, n4=None, angle_EF=0)
        
        assert_calculators_equal(orig, new, "angle_ef_zero")
    
    def test_angle_ef_ten(self):
        """angle_EF=10"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_PREMIER)
        apply_config(new, CONFIG_PREMIER)
        orig.set_directions(REV=False)
        new.set_directions(REV=False)
        
        o_pts = orig.calculate(n1=100, n2=50, n4=None, angle_EF=10)
        n_pts = new.calculate(n1=100, n2=50, n4=None, angle_EF=10)
        
        assert_calculators_equal(orig, new, "angle_ef_ten")
    
    def test_error_messages_identical(self):
        """Error messages must be identical."""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_PREMIER)
        apply_config(new, CONFIG_PREMIER)
        
        # Test "exactly 3 params" error
        try:
            orig.calculate(n1=100, n2=50, n4=120, angle_EF=5)
        except ValueError as e:
            orig_msg = str(e)
        
        try:
            new.calculate(n1=100, n2=50, n4=120, angle_EF=5)
        except ValueError as e:
            new_msg = str(e)
        
        assert orig_msg == new_msg, f"Error messages differ: '{orig_msg}' vs '{new_msg}'"
        
        # Test "angle range" error
        try:
            orig.calculate(n1=100, n2=50, n4=None, angle_EF=15)
        except ValueError as e:
            orig_msg = str(e)
        
        try:
            new.calculate(n1=100, n2=50, n4=None, angle_EF=15)
        except ValueError as e:
            new_msg = str(e)
        
        assert orig_msg == new_msg, f"Error messages differ (angle): '{orig_msg}' vs '{new_msg}'"
    
    def test_state_identical(self):
        """Initial state must be identical."""
        orig = OriginalCalculator()
        new = NewCalculator()
        
        # Reset both to empty state (load_config from file may differ)
        orig.__init__()
        new.__init__()
        
        assert orig.A_X == new.A_X
        assert orig.A_Y == new.A_Y
        assert orig.B_X == new.B_X
        assert orig.C_X == new.C_X
        assert orig.D_X == new.D_X
        assert orig.CD_LEN == new.CD_LEN
        assert orig.DE_LEN == new.DE_LEN
        assert orig.FG_LEN == new.FG_LEN
        assert orig.GH_LEN == new.GH_LEN
        assert orig.HI_LEN == new.HI_LEN
        assert orig.J_X == new.J_X
        assert orig.JK_LEN == new.JK_LEN
        assert orig.HCOR == new.HCOR
        assert orig.K_X == new.K_X
        assert orig.K_Y == new.K_Y
        assert orig.REV == new.REV
    
    def test_angle_missing(self):
        """n1=100, n2=50, n4=69.17, angle_EF=None"""
        orig = OriginalCalculator()
        new = NewCalculator()
        apply_config(orig, CONFIG_PREMIER)
        apply_config(new, CONFIG_PREMIER)
        orig.set_directions(REV=False)
        new.set_directions(REV=False)
        
        o_pts = orig.calculate(n1=100, n2=50, n4=69.17, angle_EF=None)
        n_pts = new.calculate(n1=100, n2=50, n4=69.17, angle_EF=None)
        
        assert_calculators_equal(orig, new, "angle_missing", check_n4_with_hcor=False)