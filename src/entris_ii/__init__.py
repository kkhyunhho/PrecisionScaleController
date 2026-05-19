"""Sartorius Entris-II SBI controller package.

Exports the single-class facade ``PrecisionScaleController``, modelled
on coport-uni/SyringePumpController.
"""

from entris_ii.precision_scale_controller import PrecisionScaleController

__all__ = ["PrecisionScaleController"]
