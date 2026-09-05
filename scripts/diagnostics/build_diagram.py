#!/usr/bin/env python3
"""Generic reference schematic for a lean-condition (P0171-style) signal path.

Honesty note: this is a GENERIC, principle-level reference diagram of how a
MAF/vacuum/O2 lean-condition circuit works. It is NOT a manufacturer-exact
wiring diagram for any specific make/model/year. Exact factory wiring
diagrams and pinouts require a licensed manufacturer database (e.g. AllData,
Mitchell1, factory service manuals) which RideWire does not currently have
access to. This diagram is meant to teach the mechanism, not to be used as
an as-built wiring reference.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

fig, ax = plt.subplots(figsize=(10, 6.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6.2)
ax.axis("off")

TEAL = "#01696F"
DARK = "#1B474D"
NEUTRAL = "#28251D"
BORDER = "#7A7974"
BG_BOX = "#F7F6F2"
WARN = "#964219"

def box(x, y, w, h, text, fc=BG_BOX, ec=DARK, fontsize=10.5, weight="bold", textcolor=NEUTRAL):
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    linewidth=1.4, edgecolor=ec, facecolor=fc)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fontsize, fontweight=weight, color=textcolor, wrap=True)
    return (x, y, w, h)

def arrow(b1, b2, color=DARK, label=None, style="-|>", lw=1.6, connectionstyle="arc3,rad=0.0"):
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2
    p1 = (x1 + w1, y1 + h1 / 2)
    p2 = (x2, y2 + h2 / 2)
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14,
                         color=color, lw=lw, connectionstyle=connectionstyle)
    ax.add_patch(a)
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 0.18
        ax.text(mx, my, label, ha="center", va="bottom", fontsize=8.5, color=BORDER)

# Title
ax.text(5, 6.0, "GENERIC REFERENCE: Lean Condition (P0171-style) Signal Path",
        ha="center", fontsize=13.5, fontweight="bold", color=DARK)
ax.text(5, 5.65, "Shows the PRINCIPLE of how the ECU detects/reports a lean condition - not a vehicle-specific wiring diagram",
        ha="center", fontsize=9, color=WARN, style="italic")

# Boxes - main signal path (left to right)
intake = box(0.3, 3.0, 1.8, 0.9, "Intake Air\n(unmetered if leak)", fc="#EAF4F4")
maf = box(2.6, 3.0, 1.8, 0.9, "MAF Sensor\n(measures airflow)")
pcm = box(4.9, 3.0, 1.9, 0.9, "ECU / PCM\n(compares expected\nvs. actual fuel trim)")
injectors = box(7.3, 3.0, 1.8, 0.9, "Fuel Injectors\n(fuel delivery)")

arrow(intake, maf, label="airflow")
arrow(maf, pcm, label="signal (Hz/V)")
arrow(pcm, injectors, label="injector pulse\nwidth command")

# Feedback loop - O2 sensor below
o2 = box(4.9, 1.2, 1.9, 0.9, "O2 Sensor (Bank 1)\n(measures exhaust O2)")
exhaust = box(7.3, 1.2, 1.8, 0.9, "Exhaust\n(post-combustion)")
arrow(injectors, exhaust, label="combustion")
# Route this feedback arrow below the boxes so it doesn't cross through box text
exhaust_bottom = (7.3 + 1.8 / 2, 1.2)
o2_bottom = (4.9 + 1.9 / 2, 1.2)
fb2 = FancyArrowPatch(exhaust_bottom, o2_bottom, arrowstyle="-|>", mutation_scale=14,
                       color=DARK, lw=1.6, connectionstyle="arc3,rad=0.45")
ax.add_patch(fb2)
ax.text((exhaust_bottom[0] + o2_bottom[0]) / 2, 0.55, "exhaust gas\nto O2 sensor",
        ha="center", fontsize=8.5, color=BORDER)
# reverse the visual direction manually by drawing pcm<-o2
fb = FancyArrowPatch((4.9, 1.65), (4.9, 3.0), arrowstyle="-|>", mutation_scale=14,
                      color=TEAL, lw=1.6, connectionstyle="arc3,rad=0.25")
ax.add_patch(fb)
ax.text(4.55, 2.3, "feedback:\nlean signal", ha="right", fontsize=8.5, color=TEAL)

# Vacuum leak entry point - the fault
leak = box(0.3, 0.7, 2.4, 0.8, "Possible Vacuum Leak\n(intake gasket, hose, PCV)", fc="#FBEFE9", ec=WARN, textcolor=WARN)
leak_arrow = FancyArrowPatch((1.5, 1.5), (1.5, 3.0), arrowstyle="-|>", mutation_scale=14,
                              color=WARN, lw=1.8, linestyle="--")
ax.add_patch(leak_arrow)
ax.text(1.7, 2.2, "unmetered air\nbypasses MAF", ha="left", fontsize=8.5, color=WARN)

# Result box
result = box(0.3, 4.6, 9.0, 0.7,
             "Result: PCM sees more O2 in exhaust than expected -> commands more fuel -> sets P0171 'System too Lean (Bank 1)'",
             fc="#F3F1EA", ec=BORDER, textcolor=NEUTRAL, fontsize=10)

ax.text(5, 0.15, "Reference only - always verify against the actual vehicle's factory service manual before repair.",
        ha="center", fontsize=8, color=BORDER, style="italic")

plt.tight_layout()
plt.savefig("/home/user/workspace/ridewire-action-intell/scripts/diagnostics/consensus_runs/p0171_reference_schematic.png",
            dpi=200, facecolor="white")
print("saved diagram")
