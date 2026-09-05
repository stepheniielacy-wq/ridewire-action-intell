#!/usr/bin/env python3
"""Generic reference schematics for RideWire motorcycle job aids.

Honesty note: these are GENERIC, principle-level reference diagrams showing
how each signal/circuit family works. They are NOT manufacturer-exact wiring
diagrams for any specific make/model/year. Exact factory wiring diagrams and
pinouts require a licensed manufacturer database (e.g. AllData, Mitchell1,
factory service manuals) which RideWire does not currently have access to.
These diagrams teach the mechanism, not an as-built wiring reference.

Underlying fault data is drawn from moto_codes_verified.json (Harley-Davidson
diagnostic manuals, official TSBs, and corroborating owner/technical forum
threads - see that file's "sources" and "confidence_note" fields per code).

Visual style follows build_diagram.py (the P0171 lean-condition reference):
same teal/dark-teal/neutral/warning-orange palette, FancyBboxPatch rounded
boxes, FancyArrowPatch arrows, "GENERIC REFERENCE" title treatment, italic
orange disclaimer subtitle, plain-language result box, and bottom caption.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

# ---- Shared palette (matches build_diagram.py) ----
TEAL = "#01696F"
DARK = "#1B474D"
NEUTRAL = "#28251D"
BORDER = "#7A7974"
BG_BOX = "#F7F6F2"
WARN = "#964219"

OUT_DIR = "/home/user/workspace/ridewire-action-intell/scripts/diagnostics/consensus_runs/moto"


def new_figure(width=10, height=6.6):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, height * (10 / width) if False else height)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fc=BG_BOX, ec=DARK, fontsize=10.5, weight="bold", textcolor=NEUTRAL):
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    linewidth=1.4, edgecolor=ec, facecolor=fc)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fontsize, fontweight=weight, color=textcolor, wrap=True)
    return (x, y, w, h)


def arrow(ax, b1, b2, color=DARK, label=None, style="-|>", lw=1.6,
          connectionstyle="arc3,rad=0.0", label_dy=0.30, label_side="above"):
    """Arrow from the right-center of box b1 to the left-center of box b2.

    Labels are placed ABOVE the top edge of the (taller of the two) boxes
    so they never overlap box interiors/borders, matching the no-overlap
    requirement.
    """
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2
    p1 = (x1 + w1, y1 + h1 / 2)
    p2 = (x2, y2 + h2 / 2)
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14,
                         color=color, lw=lw, connectionstyle=connectionstyle)
    ax.add_patch(a)
    if label:
        mx = (p1[0] + p2[0]) / 2
        box_top = max(y1 + h1, y2 + h2)
        if label_side == "above":
            my = box_top + label_dy
            va = "bottom"
        else:
            my = min(y1, y2) - label_dy
            va = "top"
        ax.text(mx, my, label, ha="center", va=va, fontsize=8.5, color=BORDER)
    return a


def vertical_arrow(ax, p1, p2, color=DARK, lw=1.6, connectionstyle="arc3,rad=0.0", style="-|>"):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14,
                         color=color, lw=lw, connectionstyle=connectionstyle)
    ax.add_patch(a)
    return a


def title_block(ax, title_y, subtitle_y, title_text, subtitle_text):
    ax.text(5, title_y, title_text, ha="center", fontsize=13.5, fontweight="bold", color=DARK)
    ax.text(5, subtitle_y, subtitle_text, ha="center", fontsize=9, color=WARN, style="italic")


def footer_caption(ax, y=0.15):
    ax.text(5, y, "Reference only - always verify against the actual vehicle's factory service manual before repair.",
            ha="center", fontsize=8, color=BORDER, style="italic")


def fault_entry_box(ax, x, y, w, h, text, fontsize=9.5):
    return box(ax, x, y, w, h, text, fc="#FBEFE9", ec=WARN, textcolor=WARN, fontsize=fontsize)


def dashed_warn_arrow(ax, p1, p2, connectionstyle="arc3,rad=0.0", label=None, label_pos=None):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=14,
                         color=WARN, lw=1.8, linestyle="--", connectionstyle=connectionstyle)
    ax.add_patch(a)
    if label and label_pos:
        ax.text(label_pos[0], label_pos[1], label, ha=label_pos[2] if len(label_pos) > 2 else "left",
                fontsize=8.5, color=WARN)
    return a


# =====================================================================
# 1. P0562 - Charging system
# =====================================================================
def build_p0562():
    fig, ax = new_figure(10, 6.6)

    title_block(ax, 6.35, 6.0,
                "GENERIC REFERENCE: P0562 Charging System / Battery Voltage Low",
                "Shows the PRINCIPLE of how the charging circuit is monitored - not a vehicle-specific wiring diagram")

    # Result box near top
    box(ax, 0.3, 5.15, 9.4, 0.68,
        "Result: ECM sees battery voltage stay below ~12.2V at idle and it does not rise above ~2000 RPM ->\n"
        "sets P0562 'Battery Voltage Low' and lights the speedometer battery icon",
        fc="#F3F1EA", ec=BORDER, textcolor=NEUTRAL, fontsize=9.8)

    # Main signal path - left to right, single row
    stator = box(ax, 0.3, 3.15, 1.9, 1.0, "Stator\n(generates AC current)")
    regrec = box(ax, 2.55, 3.15, 2.0, 1.0, "Voltage Regulator /\nRectifier (AC->DC,\nregulates voltage)")
    battery = box(ax, 4.9, 3.15, 1.7, 1.0, "Battery\n(stores DC power)")
    ecm = box(ax, 6.95, 3.15, 2.0, 1.0, "ECM\n(monitors battery\nvoltage over time)")

    arrow(ax, stator, regrec, label="AC voltage")
    arrow(ax, regrec, battery, label="regulated DC")
    arrow(ax, battery, ecm, label="voltage\nsense line")

    # Downstream result - speedometer warning, below/right of ECM, routed down then right to avoid crossing ecm text
    speedo = box(ax, 6.95, 1.35, 2.0, 1.0, "Speedometer\nBattery Icon\n(warning lamp)")
    ecm_bottom = (6.95 + 2.0 / 2, 3.15)
    speedo_top = (6.95 + 2.0 / 2, 1.35 + 1.0)
    vertical_arrow(ax, ecm_bottom, speedo_top, color=TEAL, connectionstyle="arc3,rad=0.0")
    ax.text(9.15, 2.25, "voltage stayed\nlow -> DTC set", ha="left", va="center", fontsize=8.5, color=TEAL)

    # Fault entry point - failed stator/reg-rectifier or corroded connections
    fault = fault_entry_box(ax, 0.3, 1.35, 4.2, 1.0,
                             "Fault entry point: failed stator, failed regulator/\n"
                             "rectifier, or loose/corroded battery & ground\n"
                             "connections (per HD bulletin M1507 diagnostics)",
                             fontsize=9.3)
    # Dashed warning arrow routed up from the fault box to a point BETWEEN stator and regrec boxes
    # (x=2.45 is the gap between stator (ends at 2.2) and regrec (starts at 2.55)), avoiding any box text
    fault_top = (2.45, 1.35 + 1.0)
    join_point = (2.45, 3.15)
    dashed_warn_arrow(ax, fault_top, join_point, connectionstyle="arc3,rad=0.0")
    ax.text(2.6, 2.25, "no/low charging\nvoltage produced", ha="left", va="center", fontsize=8.5, color=WARN)

    footer_caption(ax)
    plt.tight_layout()
    out = f"{OUT_DIR}/p0562_schematic.png"
    plt.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"saved {out}")


# =====================================================================
# 2. P0131 - Fuel injection / front O2 sensor circuit low
# =====================================================================
def build_p0131():
    fig, ax = new_figure(10, 6.6)

    title_block(ax, 6.35, 6.0,
                "GENERIC REFERENCE: P0131 Front O2 Sensor Circuit Low (Lean)",
                "Shows the PRINCIPLE of the O2 sensor feedback loop - not a vehicle-specific wiring diagram")

    box(ax, 0.3, 5.15, 9.4, 0.68,
        "Result: ECM sees a persistently low-voltage (lean) signal from the front O2 sensor ->\n"
        "commands more fuel via the front injector -> sets P0131 'Front O2 Sensor Low'",
        fc="#F3F1EA", ec=BORDER, textcolor=NEUTRAL, fontsize=9.8)

    # Main path left to right
    exhaust = box(ax, 0.3, 3.4, 2.1, 1.0, "Front Cylinder\nExhaust\n(post-combustion gas)")
    o2 = box(ax, 2.75, 3.4, 2.1, 1.0, "Front O2 Sensor\n(measures exhaust\noxygen content)")
    ecm = box(ax, 5.2, 3.4, 2.0, 1.0, "ECM\n(compares expected\nvs. actual O2 signal)")
    injector = box(ax, 7.55, 3.4, 2.15, 1.0, "Front Fuel\nInjector\n(fuel correction)")

    arrow(ax, exhaust, o2, label="O2 in\nexhaust gas")
    arrow(ax, o2, ecm, label="sensor\nvoltage (0-1V)")
    arrow(ax, ecm, injector, label="pulse width\ncorrection")

    # Feedback: injector fueling affects combustion -> affects exhaust again.
    # Routed as two straight segments dropping from directly below each box's
    # bottom-center down to a shared horizontal lane at y=2.5 (well clear of the
    # fault box below and the main row above), so it never crosses any box interior.
    lane_y = 2.5
    injector_bottom = (7.55 + 2.15 / 2, 3.4)
    exhaust_bottom = (0.3 + 2.1 / 2, 3.4)
    drop_right = (injector_bottom[0], lane_y)
    drop_left = (exhaust_bottom[0], lane_y)
    down1 = FancyArrowPatch(injector_bottom, drop_right, arrowstyle="-", mutation_scale=14,
                             color=TEAL, lw=1.6)
    across = FancyArrowPatch(drop_right, drop_left, arrowstyle="-", mutation_scale=14,
                              color=TEAL, lw=1.6)
    up2 = FancyArrowPatch(drop_left, exhaust_bottom, arrowstyle="-|>", mutation_scale=14,
                           color=TEAL, lw=1.6)
    ax.add_patch(down1)
    ax.add_patch(across)
    ax.add_patch(up2)
    ax.text(5, lane_y + 0.16, "corrected fuel changes combustion / exhaust O2 (closed-loop feedback)",
            ha="center", va="bottom", fontsize=8.5, color=TEAL)

    # Fault entry point - exhaust leak near O2 sensor
    fault = fault_entry_box(ax, 0.3, 0.55, 4.55, 1.0,
                             "Fault entry point: exhaust leak near front O2 sensor\n"
                             "or head pipe (cracked header / loose flange) draws\n"
                             "in outside air, reading falsely lean",
                             fontsize=9.3)
    fault_top = (0.3 + 4.55 / 2, 0.55 + 1.0)
    # Route straight up into the gap between the exhaust box and the O2 sensor box
    # (x=2.6 sits in the empty gap: exhaust box ends at 2.4, O2 box starts at 2.75),
    # well clear of the feedback arc/label which stay to the right and lower.
    gap_x = 2.6
    dashed_warn_arrow(ax, fault_top, (gap_x, 3.4), connectionstyle="arc3,rad=0.0")
    ax.text(2.75, 1.75, "outside air\nbypasses sensor", ha="left", va="center", fontsize=8.5, color=WARN)

    footer_caption(ax)
    plt.tight_layout()
    out = f"{OUT_DIR}/p0131_schematic.png"
    plt.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"saved {out}")


# =====================================================================
# 3. CKP - Crankshaft position sensor circuit (P0371/P0372/P0374)
# =====================================================================
def build_ckp():
    fig, ax = new_figure(10, 6.6)

    title_block(ax, 6.35, 6.0,
                "GENERIC REFERENCE: CKP Circuit (P0371 / P0372 / P0374)",
                "Shows the PRINCIPLE of the crank position signal path - not a vehicle-specific wiring diagram")

    box(ax, 0.3, 5.15, 9.4, 0.68,
        "Result: ICM sees a weak, shorted, or absent CKP signal (not >=1 VAC while cranking) ->\n"
        "cannot synchronize spark timing -> sets P0371/P0372 (signal shorted low/high) or P0374 (not detected)",
        fc="#F3F1EA", ec=BORDER, textcolor=NEUTRAL, fontsize=9.6)

    crank = box(ax, 0.3, 3.15, 2.1, 1.0, "Crankshaft\nRotation\n(engine position)")
    ckp = box(ax, 2.75, 3.15, 2.1, 1.0, "CKP Sensor\n(AC signal\ngenerator)")
    icm = box(ax, 5.2, 3.15, 2.0, 1.0, "Ignition Control\nModule (ICM)")
    spark = box(ax, 7.55, 3.15, 2.15, 1.0, "Spark Timing\nOutput\n(coil trigger)")

    arrow(ax, crank, ckp, label="rotation")
    arrow(ax, ckp, icm, label="AC signal\n(>=1 VAC)")
    arrow(ax, icm, spark, label="timed spark\ncommand")

    # Fault entry point - pinched/damaged wiring or loose sensor mount
    fault = fault_entry_box(ax, 0.3, 0.9, 4.55, 1.0,
                             "Fault entry point: pinched/damaged CKP sensor\n"
                             "wiring, loose sensor mounting fastener, or a\n"
                             "wiring short to ground/voltage",
                             fontsize=9.3)
    fault_top = (0.3 + 4.55 / 2, 0.9 + 1.0)
    gap_x = 2.6  # gap between crank box (ends 2.4) and ckp box (starts 2.75)
    dashed_warn_arrow(ax, fault_top, (gap_x, 3.15), connectionstyle="arc3,rad=-0.1")
    ax.text(2.75, 2.15, "signal weak,\nshorted, or lost", ha="left", va="center", fontsize=8.5, color=WARN)

    footer_caption(ax)
    plt.tight_layout()
    out = f"{OUT_DIR}/ckp_schematic.png"
    plt.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"saved {out}")


# =====================================================================
# 4. C1032/C1034 - ABS wheel speed sensor circuit
# =====================================================================
def build_abs():
    fig, ax = new_figure(10, 6.6)

    title_block(ax, 6.35, 6.0,
                "GENERIC REFERENCE: C1032 / C1034 Wheel Speed Sensor Circuit",
                "Shows the PRINCIPLE of the ABS wheel speed circuit - not a vehicle-specific wiring diagram")

    box(ax, 0.3, 5.15, 9.4, 0.68,
        "Result: ABS module detects an open or shorted wheel speed sensor circuit (front=C1032, rear=C1034) ->\n"
        "disables ABS function and illuminates the dash ABS indicator",
        fc="#F3F1EA", ec=BORDER, textcolor=NEUTRAL, fontsize=9.8)

    wheel = box(ax, 0.3, 3.15, 2.1, 1.0, "Wheel + Tone\nRing Rotation")
    wss = box(ax, 2.75, 3.15, 2.1, 1.0, "Wheel Speed\nSensor\n(front or rear)")
    absmod = box(ax, 5.2, 3.15, 2.0, 1.0, "ABS Module\n(checks circuit\nhi/lo side)")
    output = box(ax, 7.55, 3.15, 2.15, 1.0, "ABS Enable/Disable\n+ Dash Indicator")

    arrow(ax, wheel, wss, label="rotation")
    arrow(ax, wss, absmod, label="speed\npulse signal")
    arrow(ax, absmod, output, label="fault status")

    # Fault entry point - broken/pinched sensor wire at steering neck (front) or similar (rear)
    fault = fault_entry_box(ax, 0.3, 0.9, 4.55, 1.0,
                             "Fault entry point: broken or pinched wheel speed\n"
                             "sensor wire, most often at the steering neck/fork\n"
                             "area (front) or similar chafe points (rear)",
                             fontsize=9.3)
    fault_top = (0.3 + 4.55 / 2, 0.9 + 1.0)
    gap_x = 2.6  # gap between wheel box (ends 2.4) and wss box (starts 2.75)
    dashed_warn_arrow(ax, fault_top, (gap_x, 3.15), connectionstyle="arc3,rad=-0.1")
    ax.text(2.75, 2.15, "open/shorted\ncircuit", ha="left", va="center", fontsize=8.5, color=WARN)

    footer_caption(ax)
    plt.tight_layout()
    out = f"{OUT_DIR}/abs_schematic.png"
    plt.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"saved {out}")


if __name__ == "__main__":
    import os
    os.makedirs(OUT_DIR, exist_ok=True)
    build_p0562()
    build_p0131()
    build_ckp()
    build_abs()
    print("all diagrams saved")
