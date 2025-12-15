#!/usr/bin/env python3
"""Generate a modern kernel bandwidth comparison figure for GWR notebook."""

import matplotlib.pyplot as plt
import numpy as np

# Set up style
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def bisquare_kernel(d, bandwidth):
    """Bisquare (bi-weight) kernel: compact support."""
    w = np.zeros_like(d)
    mask = np.abs(d) <= bandwidth
    w[mask] = (1 - (d[mask] / bandwidth) ** 2) ** 2
    return w


def gaussian_kernel(d, bandwidth):
    """Gaussian kernel: infinite support."""
    return np.exp(-0.5 * (d / bandwidth) ** 2)


# Distance values
d = np.linspace(-3, 3, 500)
bandwidth = 1.0

# Calculate weights
w_bisquare = bisquare_kernel(d, bandwidth)
w_gaussian = gaussian_kernel(d, bandwidth)

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

# Colors
color_bisquare = "#2166ac"  # blue
color_gaussian = "#b2182b"  # red
color_bandwidth = "#666666"

for ax, kernel_func, w, name, color in [
    (axes[0], bisquare_kernel, w_bisquare, "Bisquare", color_bisquare),
    (axes[1], gaussian_kernel, w_gaussian, "Gaussian", color_gaussian),
]:
    # Plot kernel
    ax.fill_between(d, w, alpha=0.3, color=color)
    ax.plot(d, w, color=color, linewidth=2.5, label=name)

    # Bandwidth markers
    ax.axvline(
        -bandwidth, color=color_bandwidth, linestyle="--", linewidth=1, alpha=0.7
    )
    ax.axvline(bandwidth, color=color_bandwidth, linestyle="--", linewidth=1, alpha=0.7)

    # Bandwidth annotation
    ax.annotate(
        "",
        xy=(bandwidth, 0.55),
        xytext=(-bandwidth, 0.55),
        arrowprops=dict(arrowstyle="<->", color=color_bandwidth, lw=1.5),
    )
    ax.text(
        0,
        0.58,
        "bandwidth",
        ha="center",
        va="bottom",
        fontsize=10,
        color=color_bandwidth,
    )

    # Regression point
    ax.plot(0, 0, "ko", markersize=10, zorder=5)
    ax.annotate(
        "regression\npoint",
        xy=(0, 0),
        xytext=(0, 0.15),
        ha="center",
        va="bottom",
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
    )

    # Sample data points
    sample_points = [-0.4, 0.7, 1.5, 2.2]
    for sp in sample_points:
        weight = kernel_func(np.array([sp]), bandwidth)[0]
        ax.plot(sp, 0, "o", color="#333333", markersize=6, zorder=4)
        if weight > 0.01:
            ax.plot([sp, sp], [0, weight], ":", color="#888888", linewidth=1)
            ax.plot(sp, weight, "o", color=color, markersize=5, zorder=5)

    ax.set_xlabel("Distance from regression point ($d_{ij}$)")
    ax.set_xlim(-3, 3)
    ax.set_ylim(-0.15, 1.1)
    ax.set_title(f"{name} Kernel", fontweight="bold")

    # Add key insight annotation
    if name == "Bisquare":
        ax.annotate(
            "Weight = 0\n(exactly)",
            xy=(1.8, 0),
            xytext=(2.3, 0.25),
            fontsize=9,
            ha="center",
            color=color_bandwidth,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", edgecolor="none"),
            arrowprops=dict(arrowstyle="->", color=color_bandwidth, lw=0.8),
        )
    else:
        ax.annotate(
            "Weight > 0\n(always)",
            xy=(2.2, 0.028),
            xytext=(2.3, 0.25),
            fontsize=9,
            ha="center",
            color=color_bandwidth,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", edgecolor="none"),
            arrowprops=dict(arrowstyle="->", color=color_bandwidth, lw=0.8),
        )

axes[0].set_ylabel("Weight ($w_{ij}$)")

# Add formula annotations
axes[0].text(
    0,
    -0.38,
    r"$w_{ij} = \left(1 - \left(\frac{d_{ij}}{b}\right)^2\right)^2$ if $d_{ij} \leq b$, else 0",
    ha="center",
    fontsize=10,
    transform=axes[0].transData,
)
axes[1].text(
    0,
    -0.38,
    r"$w_{ij} = \exp\left(-\frac{1}{2}\left(\frac{d_{ij}}{b}\right)^2\right)$",
    ha="center",
    fontsize=10,
    transform=axes[1].transData,
)

plt.tight_layout()
plt.savefig(
    "kernel_bandwidth.png",
    dpi=150,
    bbox_inches="tight",
    facecolor="white",
    edgecolor="none",
)
plt.savefig(
    "kernel_bandwidth.svg",
    bbox_inches="tight",
    facecolor="white",
    edgecolor="none",
)
