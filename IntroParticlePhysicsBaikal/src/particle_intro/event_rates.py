"""Toy event-rate utilities."""


def expected_events(flux, cross_section, n_targets, exposure_time, efficiency=1.0):
    """Return expected event count in a simple counting experiment."""
    return flux * cross_section * n_targets * exposure_time * efficiency


def interaction_length(number_density, cross_section):
    """Return interaction length 1/(n sigma)."""
    return 1.0 / (number_density * cross_section)

