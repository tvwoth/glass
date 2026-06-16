"""
Custom exceptions for the calculation core.
"""


class CalculationError(Exception):
    """Base exception for calculation errors."""
    pass


class ParameterCountError(CalculationError):
    """Raised when the number of provided parameters is incorrect."""
    pass


class ParameterRangeError(CalculationError):
    """Raised when a parameter is outside its valid range."""
    pass


class ConfigError(CalculationError):
    """Raised when configuration is invalid."""
    pass


class SolverError(CalculationError):
    """Raised when a solver fails to find a solution."""
    pass