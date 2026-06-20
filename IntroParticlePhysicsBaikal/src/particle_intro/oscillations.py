"""Two-flavor vacuum neutrino oscillation utilities."""

import numpy as np


def two_flavor_transition_probability(L_km, E_GeV, dm2_eV2, theta):
    """Two-flavor vacuum oscillation probability."""
    phase = 1.267 * dm2_eV2 * np.asarray(L_km) / E_GeV
    return np.sin(2.0 * theta) ** 2 * np.sin(phase) ** 2


def two_flavor_survival_probability(L_km, E_GeV, dm2_eV2, theta):
    """Two-flavor vacuum survival probability."""
    return 1.0 - two_flavor_transition_probability(L_km, E_GeV, dm2_eV2, theta)

