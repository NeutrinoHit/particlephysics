"""Plot helpers for short pedagogical notebooks."""

import numpy as np

from .decay import survival_probability
from .event_rates import expected_events
from .oscillations import two_flavor_survival_probability


def plot_event_rate_scaling(ax, cross_sections, flux, n_targets, exposure_time, efficiency=1.0):
    """Plot expected event count as a function of cross section."""
    counts = expected_events(
        flux=flux,
        cross_section=np.asarray(cross_sections),
        n_targets=n_targets,
        exposure_time=exposure_time,
        efficiency=efficiency,
    )
    ax.loglog(cross_sections, counts)
    ax.set_xlabel(r"cross section $\sigma$ [cm$^2$]")
    ax.set_ylabel(r"expected events $N$")
    ax.grid(True, which="both", alpha=0.3)
    return ax


def plot_decay_law(ax, t, taus):
    """Plot exponential survival probability for several lifetimes."""
    for tau in taus:
        ax.plot(t, survival_probability(t, tau), label=rf"$\tau={tau:g}$")
    ax.set_xlabel(r"time $t$")
    ax.set_ylabel(r"survival probability $P(t)$")
    ax.grid(True, alpha=0.3)
    ax.legend()
    return ax


def plot_oscillation_probability(ax, L_over_E, dm2_eV2, theta):
    """Plot two-flavor muon-neutrino survival probability versus L/E."""
    probability = two_flavor_survival_probability(
        L_km=np.asarray(L_over_E),
        E_GeV=1.0,
        dm2_eV2=dm2_eV2,
        theta=theta,
    )
    ax.semilogx(L_over_E, probability)
    ax.set_xlabel(r"$L/E$ [km/GeV]")
    ax.set_ylabel(r"$P_{\nu_\mu\to\nu_\mu}$")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, which="both", alpha=0.3)
    return ax

