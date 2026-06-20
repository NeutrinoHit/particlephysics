"""Toy exponential decay utilities."""

import numpy as np


def survival_probability(t, tau):
    """Exponential survival probability exp(-t/tau)."""
    return np.exp(-np.asarray(t) / tau)


def decay_pdf(t, tau):
    """Decay time probability density."""
    return survival_probability(t, tau) / tau

