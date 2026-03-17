#!/usr/bin/env python3
"""Generate conceptual diagrams for the Truth Post paper.

Produces:
  diagrams/fig-claim-states.png          Claim state machine
  diagrams/fig-actor-flow.png            Actor interaction flow
  diagrams/fig-architecture.png          Protocol architecture layers
  diagrams/fig-relevance-round.png       Relevance round sequence
  diagrams/fig-framework.png             Four-step framework pipeline
  diagrams/fig-falsifiability.png        Falsifiability spectrum
  diagrams/fig-confidence-reputation.png Confidence vs reputation trajectories
  diagrams/fig-pool-economics.png        Pool economics money flow
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import matplotlib.font_manager as fm
import numpy as np
import os

# ── PUW brand font ──
# Prefer Space Mono if installed; fall back to generic monospace.
_MONO_CANDIDATES = ['Space Mono', 'monospace']
_available = {f.name for f in fm.fontManager.ttflist}
_font = next((f for f in _MONO_CANDIDATES if f in _available), 'monospace')
plt.rcParams.update({
    'font.family': _font,
    'mathtext.default': 'regular',
})

# ── PUW brand colors ──
C = dict(
    bg='#171717',
    text='#ececec', box='#1f1f1f', edge='#505050',
    term='#2a2a2a', term_e='#ff355e', accent='#ff355e',
    arrow='#727272', L1='#1f1f1f', L2='#2a2a2a', L3='#333333',
)


def _ep(cx, cy, w, h, tx, ty):
    """Edge point of rect centered at (cx,cy) toward (tx,ty)."""
    dx, dy = tx - cx, ty - cy
    if abs(dx) < 1e-10 and abs(dy) < 1e-10:
        return cx, cy
    sc = []
    if abs(dx) > 1e-10:
        sc.append((w / 2) / abs(dx))
    if abs(dy) > 1e-10:
        sc.append((h / 2) / abs(dy))
    t = min(sc)
    return cx + t * dx, cy + t * dy


def _box(ax, cx, cy, w, h, label, term=False, fill=None, ec=None,
         fs=10, bold=True, lw=1.5, zorder=2):
    """Rounded rectangle with centered label. Double border for terminal states."""
    fill = fill or (C['term'] if term else C['box'])
    ec = ec or (C['term_e'] if term else C['edge'])
    p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                       boxstyle='round,pad=0.06', fc=fill, ec=ec,
                       lw=2.0 if term else lw, zorder=zorder)
    ax.add_patch(p)
    if term:
        ax.add_patch(FancyBboxPatch(
            (cx - w / 2 + 0.07, cy - h / 2 + 0.05),
            w - 0.14, h - 0.10,
            boxstyle='round,pad=0.04', fc='none', ec=ec,
            lw=0.8, zorder=zorder + 1))
    ax.text(cx, cy, label, fontsize=fs,
            fontweight='bold' if bold else 'normal',
            color=C['text'], ha='center', va='center', zorder=zorder + 2)


def _arr(ax, x0, y0, x1, y1, label='', rad=0., lo=(0, 0), fs=8,
         color=None, style='->'):
    """Arrow with optional label at midpoint."""
    color = color or C['arrow']
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color,
                               connectionstyle=f'arc3,rad={rad}',
                               lw=1.2, mutation_scale=14),
                zorder=1)
    if label:
        ax.text((x0 + x1) / 2 + lo[0], (y0 + y1) / 2 + lo[1], label,
                fontsize=fs, color=color, ha='center', va='center',
                zorder=10,
                bbox=dict(boxstyle='round,pad=0.12', fc=C['bg'],
                          ec='none', alpha=0.9))


# ══════════════════════════════════════════════════════════
# 1. Claim State Machine
# ══════════════════════════════════════════════════════════
def fig1_claim_states(out):
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(-1.5, 13.5)
    ax.set_ylim(0, 9.5)
    ax.set_aspect('equal')
    ax.axis('off')

    W, H = 2.8, 0.75
    P = {
        'Live':            (5.5, 7.5),
        'PendingEdit':     (1.2, 5.5),
        'WithdrawPending': (1.2, 3.0),
        'Challenged':      (10.0, 5.5),
        'Withdrawn':       (1.2, 0.9),
        'Closed':          (10.0, 0.9),
    }

    for n, (cx, cy) in P.items():
        _box(ax, cx, cy, W, H, n, term=n in ('Withdrawn', 'Closed'))

    # ── Initial dot → Live ──
    ax.plot(5.5, 8.9, 'o', color=C['text'], ms=9, zorder=5)
    _arr(ax, 5.5, 8.78, 5.5, P['Live'][1] + H / 2 + 0.02,
         'post claim + lock bond', lo=(1.6, 0), fs=7)

    # ── Live → PendingEdit ──
    s = _ep(*P['Live'], W, H, *P['PendingEdit'])
    t = _ep(*P['PendingEdit'], W, H, *P['Live'])
    _arr(ax, *s, *t, 'author amends\n(confidence paused)',
         rad=-0.15, lo=(-0.3, 0.35), fs=7)

    # ── PendingEdit → Live ──
    _arr(ax, *t, *s, 'edit finalized\n(confidence resets)',
         rad=-0.15, lo=(0.3, -0.35), fs=7)

    # ── Live → Challenged ──
    s = _ep(*P['Live'], W, H, *P['Challenged'])
    t = _ep(*P['Challenged'], W, H, *P['Live'])
    _arr(ax, *s, *t, 'challenge filed\n(confidence paused)',
         rad=0.15, lo=(0.3, 0.35), fs=7)

    # ── Challenged → Live ──
    _arr(ax, *t, *s, 'challenge fails\n(confidence resumes)',
         rad=0.15, lo=(-0.3, -0.35), fs=7)

    # ── PendingEdit → Challenged ──
    s = _ep(*P['PendingEdit'], W, H, *P['Challenged'])
    t = _ep(*P['Challenged'], W, H, *P['PendingEdit'])
    _arr(ax, *s, *t, 'challenge on\nold revision',
         lo=(0, 0.35), fs=7)

    # ── Challenged → PendingEdit ──
    _arr(ax, *t, *s, 'defense;\nresume edit',
         lo=(0, -0.35), fs=7)

    # ── Live → WithdrawPending ──
    s = _ep(*P['Live'], W, H, *P['WithdrawPending'])
    t = _ep(*P['WithdrawPending'], W, H, *P['Live'])
    _arr(ax, *s, *t, 'author\nwithdraws',
         rad=0.0, lo=(-1.8, -0.5), fs=7)

    # ── WithdrawPending → Challenged ──
    s = _ep(*P['WithdrawPending'], W, H, *P['Challenged'])
    t = _ep(*P['Challenged'], W, H, *P['WithdrawPending'])
    _arr(ax, *s, *t, 'challenge during\ncooldown', lo=(0, -0.35), fs=7)

    # ── WithdrawPending → Withdrawn ──
    s = _ep(*P['WithdrawPending'], W, H, *P['Withdrawn'])
    t = _ep(*P['Withdrawn'], W, H, *P['WithdrawPending'])
    _arr(ax, *s, *t, 'cooldown expires\n(confidence frozen)',
         lo=(-1.6, 0), fs=7)

    # ── Challenged → Closed ──
    s = _ep(*P['Challenged'], W, H, *P['Closed'])
    t = _ep(*P['Closed'], W, H, *P['Challenged'])
    _arr(ax, *s, *t, 'debunked\n(bond transferred)',
         lo=(1.6, 0), fs=7)

    # ── Challenged → Challenged (self-loop for queued challenges) ──
    ax.annotate('', xy=(P['Challenged'][0] + W / 2 + 0.05, P['Challenged'][1] + 0.1),
                xytext=(P['Challenged'][0] + W / 2 + 0.05, P['Challenged'][1] - 0.1),
                arrowprops=dict(arrowstyle='->', color=C['arrow'],
                               connectionstyle='arc3,rad=-1.8',
                               lw=1.2, mutation_scale=14), zorder=1)
    ax.text(P['Challenged'][0] + W / 2 + 0.9, P['Challenged'][1],
            'queued\nchallenge', fontsize=6, color=C['arrow'],
            ha='left', va='center')

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor=C['bg'], pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 2. Actor Interaction Flow
# ══════════════════════════════════════════════════════════
def fig2_actor_flow(out):
    fig, ax = plt.subplots(figsize=(13, 7), dpi=300)
    ax.set_xlim(-0.5, 13.0)
    ax.set_ylim(-0.5, 7.5)
    ax.axis('off')

    # Central protocol column
    pw, ph = 3.4, 5.5
    pcx, pcy = 6.0, 3.5
    ax.add_patch(FancyBboxPatch(
        (pcx - pw / 2, pcy - ph / 2), pw, ph,
        boxstyle='round,pad=0.12', fc=C['L1'], ec=C['accent'],
        lw=2, zorder=1))
    ax.text(pcx, pcy + ph / 2 - 0.35, 'Protocol',
            fontsize=13, fontweight='bold', color=C['accent'],
            ha='center', va='center', zorder=4)

    # Sub-components inside protocol
    subs = ['Pools', 'Claims & Bonds', 'Challenge State', 'Relevance Rounds']
    for i, s in enumerate(subs):
        sy = pcy + 1.2 - i * 0.9
        _box(ax, pcx, sy, 3.0, 0.55, s, fs=8, bold=False,
             fill=C['L2'], ec=C['edge'])

    # Left-side actors
    AW, AH = 2.4, 0.65
    left_actors = [
        ('Authors',       6.2),
        ('Challengers',   4.5),
        ('Curators',      2.8),
        ('Pool Creators', 1.1),
    ]
    for name, y in left_actors:
        _box(ax, 1.5, y, AW, AH, name, fs=9)

    # Right-side actors
    right_actors = [
        ('Jurors (DDR)',          5.5),
        ('Interface\nOperators', 2.0),
    ]
    for name, y in right_actors:
        _box(ax, 11.2, y, AW, AH, name, fs=9)

    # Arrows: left actors → protocol
    left_flows = [
        (6.2, 5.7, 'post claims\n+ bonds'),
        (4.5, 4.0, 'file challenges\n+ counter-stake'),
        (2.8, 2.5, 'stake +\ncommit/reveal'),
        (1.1, 1.3, 'define pool\nconfig'),
    ]
    for ay, py, lbl in left_flows:
        _arr(ax, 1.5 + AW / 2, ay, pcx - pw / 2, py,
             lbl, lo=(0, 0.35), fs=7)

    # Arrows: protocol ↔ jurors
    _arr(ax, pcx + pw / 2, 5.2, 11.2 - AW / 2, 5.7,
         'disputes', lo=(0, 0.22), fs=7)
    _arr(ax, 11.2 - AW / 2, 5.3, pcx + pw / 2, 4.6,
         'verdicts', lo=(0, -0.22), fs=7)

    # Arrow: protocol → interface operators
    _arr(ax, pcx + pw / 2, 2.0, 11.2 - AW / 2, 2.0,
         'read canonical state,\nrender feeds', lo=(0, 0.35), fs=7)

    # Annotation
    ax.text(pcx, pcy - ph / 2 - 0.35,
            'challenge tax \u2192 pool reward budget',
            fontsize=8, fontstyle='italic', color=C['accent'],
            ha='center', va='top')

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor=C['bg'], pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 3. Protocol Architecture Layers
# ══════════════════════════════════════════════════════════
def fig3_architecture(out):
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(-1.0, 8.5)
    ax.axis('off')

    layers = [
        ('Interfaces (replaceable)',
         5.8, C['L3'],
         'Any frontend: feeds, dashboards,\ndispute history, pool browsers'),
        ('Content & Indexing\n(off-chain, reconstructible)',
         3.8, C['L2'],
         'Claim blobs, evidence items,\npolicy documents, indexers'),
        ('External DDR\n(Kleros v1)',
         1.8, C['L2'],
         'Binary challenge adjudication,\ntyped reasons, appeals'),
        ('Canonical Protocol State\n(on-chain)',
         -0.2, C['L1'],
         'Pools, claim refs, stakes, challenges,\nadjudication links, confidence, payouts'),
    ]

    lw_box, lh_box = 9.6, 1.4
    lx = 1.2
    for title, cy, color, desc in layers:
        ax.add_patch(FancyBboxPatch(
            (lx, cy - lh_box / 2), lw_box, lh_box,
            boxstyle='round,pad=0.1', fc=color, ec=C['edge'],
            lw=1.5, zorder=2))
        ax.text(lx + 0.3, cy + 0.25, title, fontsize=9,
                fontweight='bold', color=C['text'], va='center', zorder=4)
        ax.text(lx + 0.3, cy - 0.3, desc, fontsize=7,
                fontstyle='italic', color='#999999', va='center', zorder=4)

    # Inter-layer arrows
    mid_x = lx + lw_box / 2
    _arr(ax, mid_x, 5.8 - lh_box / 2, mid_x, 3.8 + lh_box / 2)
    _arr(ax, mid_x, 3.8 - lh_box / 2, mid_x, 1.8 + lh_box / 2)
    _arr(ax, mid_x, 1.8 - lh_box / 2, mid_x, -0.2 + lh_box / 2)

    # Architectural commitments (top left)
    ax.text(1.2, 7.4, 'Architectural commitments', fontsize=9,
            fontweight='bold', color=C['accent'])
    for i, c in enumerate([
        'Permissionless pools',
        'Immutable contracts',
        'Minimal governance',
    ]):
        ax.text(1.5, 7.0 - i * 0.35, '\u2022  ' + c, fontsize=8,
                color=C['text'])

    # Pool economics (top right)
    ax.text(6.5, 7.4, 'Pool economics', fontsize=9,
            fontweight='bold', color=C['accent'])
    for i, c in enumerate([
        'Local reward budgets',
        'Challenge tax \u2192 pool budget',
        'No global treasury',
    ]):
        ax.text(6.8, 7.0 - i * 0.35, '\u2022  ' + c, fontsize=8,
                color=C['text'])

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor=C['bg'], pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 4. Relevance Round Sequence
# ══════════════════════════════════════════════════════════
def fig4_relevance_round(out):
    fig, ax = plt.subplots(figsize=(8, 10), dpi=300)
    ax.set_xlim(0, 8)
    ax.set_ylim(-0.5, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    steps = [
        ('1', 'Curators stake into pool'),
        ('2', 'Round scheduled for Live item\nat pool-defined cadence'),
        ('3', r'Stake-weighted draft: $d_i = s_i$'),
        ('4', 'Drafted curators commit/reveal\nscores in [0, 1]'),
        ('5', r'Weight capping:'
              '\n'
              r'$w_i = \min(s_i,\; c \cdot \mathrm{total\_stake})$'),
        ('6', r'Coherence check:'
              '\n'
              r'slash if $|v_i - \mu| > K\sigma$'),
        ('7', 'Near-flat rounds cancelled\nas degenerate'),
    ]

    cx = 4.3
    bw, bh = 5.8, 0.85
    y0 = 9.0
    gap = 1.3

    for i, (num, text) in enumerate(steps):
        cy = y0 - i * gap

        # Number circle
        ncx = cx - bw / 2 - 0.45
        circ = plt.Circle((ncx, cy), 0.22, fc=C['accent'],
                          ec='none', zorder=5)
        ax.add_patch(circ)
        ax.text(ncx, cy, num, fontsize=10, fontweight='bold',
                color='white', ha='center', va='center', zorder=6)

        _box(ax, cx, cy, bw, bh, text, fs=8, bold=False)

        # Arrow to next step
        if i < len(steps) - 1:
            _arr(ax, cx, cy - bh / 2, cx, cy - gap + bh / 2)

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor=C['bg'], pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 5. Four-Step Framework Pipeline
# ══════════════════════════════════════════════════════════
def fig5_framework(out):
    fig, ax = plt.subplots(figsize=(12, 11), dpi=300)
    ax.set_xlim(-1.5, 12.5)
    ax.set_ylim(-1.5, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')

    cx = 5.5
    bw, bh = 5.8, 0.85
    y0 = 10.5
    gap = 1.4

    # ── Steps 1, 2 (regular boxes) ──
    reg_steps = [
        ('1', 'Identify hidden curation problem'),
        ('2', 'Determine quality dimensions'),
    ]
    for i, (num, text) in enumerate(reg_steps):
        cy = y0 - i * gap
        ncx = cx - bw / 2 - 0.45
        circ = plt.Circle((ncx, cy), 0.22, fc=C['accent'],
                          ec='none', zorder=5)
        ax.add_patch(circ)
        ax.text(ncx, cy, num, fontsize=10, fontweight='bold',
                color='white', ha='center', va='center', zorder=6)
        _box(ax, cx, cy, bw, bh, text, fs=9, bold=False)
        # Arrow to next step
        _arr(ax, cx, cy - bh / 2, cx, cy - gap + bh / 2)

    # ── Step 3: diamond gate ──
    s3y = y0 - 2 * gap
    dw, dh = 2.8, 0.8  # half-widths
    diamond_verts = [
        (cx, s3y + dh),       # top
        (cx + dw, s3y),       # right
        (cx, s3y - dh),       # bottom
        (cx - dw, s3y),       # left
    ]
    diamond = Polygon(diamond_verts, closed=True,
                      fc=C['box'], ec=C['accent'], lw=2.0, zorder=2)
    ax.add_patch(diamond)
    ax.text(cx, s3y, 'Falsification\nfeasible?', fontsize=9,
            fontweight='normal', color=C['text'],
            ha='center', va='center', zorder=4)

    # Number circle for step 3 at left vertex offset
    ncx3 = cx - dw - 0.45
    circ3 = plt.Circle((ncx3, s3y), 0.22, fc=C['accent'],
                       ec='none', zorder=5)
    ax.add_patch(circ3)
    ax.text(ncx3, s3y, '3', fontsize=10, fontweight='bold',
            color='white', ha='center', va='center', zorder=6)

    # "Out of scope" branch from right vertex
    oos_x = cx + dw + 1.8
    _arr(ax, cx + dw, s3y, oos_x - 0.1, s3y, fs=7)
    ax.text(oos_x, s3y, 'Out of scope', fontsize=8, fontstyle='italic',
            color=C['accent'], ha='left', va='center', zorder=4)

    # Arrow from diamond bottom to step 4
    s4y = y0 - 3 * gap
    _arr(ax, cx, s3y - dh, cx, s4y + bh / 2)

    # ── Step 4 (regular box) ──
    ncx4 = cx - bw / 2 - 0.45
    circ4 = plt.Circle((ncx4, s4y), 0.22, fc=C['accent'],
                       ec='none', zorder=5)
    ax.add_patch(circ4)
    ax.text(ncx4, s4y, '4', fontsize=10, fontweight='bold',
            color='white', ha='center', va='center', zorder=6)
    _box(ax, cx, s4y, bw, bh, 'Design per-dimension mechanisms',
         fs=9, bold=False)

    # ── Dashed boundary between framework and instantiation ──
    boundary_y = s4y - bh / 2 - 0.6
    ax.plot([-0.5, 11.5], [boundary_y, boundary_y],
            color=C['edge'], lw=1.0, linestyle='--', zorder=1)

    # Zone labels on left margin
    framework_mid_y = (y0 + s4y) / 2
    ax.text(-1.2, framework_mid_y, 'FRAMEWORK', fontsize=7,
            fontweight='bold', color=C['edge'], ha='center', va='center',
            rotation=90, zorder=4)
    inst_mid_y = boundary_y - 2.0
    ax.text(-1.2, inst_mid_y, 'INSTANTIATION', fontsize=7,
            fontweight='bold', color=C['edge'], ha='center', va='center',
            rotation=90, zorder=4)

    # ── Instantiation section ──
    left_x = 3.2
    right_x = 8.2
    header_y = boundary_y - 1.0
    leaf_bw = 4.2
    leaf_bh = 0.75
    header_bh = 0.7
    leaf_gap = 1.0

    # Branching arrows from step 4 to headers
    _arr(ax, cx - 0.8, s4y - bh / 2, left_x, header_y + header_bh / 2)
    _arr(ax, cx + 0.8, s4y - bh / 2, right_x, header_y + header_bh / 2)

    # --- News column (left, accent border) ---
    _box(ax, left_x, header_y, 2.0, header_bh, 'News',
         fs=10, bold=True, fill=C['L1'], ec=C['accent'])

    leaf1_y = header_y - leaf_gap
    leaf2_y = header_y - 2 * leaf_gap
    _arr(ax, left_x, header_y - header_bh / 2,
         left_x, leaf1_y + leaf_bh / 2)
    _box(ax, left_x, leaf1_y, leaf_bw, leaf_bh,
         'Accuracy: bonded publication\n+ open challenge',
         fs=7.5, bold=False, fill=C['L1'], ec=C['accent'])

    _arr(ax, left_x, leaf1_y - leaf_bh / 2,
         left_x, leaf2_y + leaf_bh / 2)
    _box(ax, left_x, leaf2_y, leaf_bw, leaf_bh,
         'Relevance: drafted curator rounds\n+ coherence slashing',
         fs=7.5, bold=False, fill=C['L1'], ec=C['accent'])

    # --- Advertising column (right, grey border) ---
    _box(ax, right_x, header_y, 2.8, header_bh, 'Advertising',
         fs=10, bold=True, fill=C['L2'], ec=C['edge'])

    ad_leaf_y = header_y - leaf_gap
    _arr(ax, right_x, header_y - header_bh / 2,
         right_x, ad_leaf_y + leaf_bh / 2)
    _box(ax, right_x, ad_leaf_y, leaf_bw, leaf_bh,
         'Truthfulness: bonded claims',
         fs=7.5, bold=False, fill=C['L2'], ec=C['edge'])

    # ── Bottom annotation ──
    bottom_y = min(leaf2_y, ad_leaf_y) - leaf_bh / 2 - 0.4
    ax.text(cx, bottom_y,
            'Same framework, different decompositions',
            fontsize=8, fontstyle='italic', color=C['accent'],
            ha='center', va='top')

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor=C['bg'], pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 6. Falsifiability Spectrum
# ══════════════════════════════════════════════════════════
def fig6_falsifiability(out):
    fig, ax = plt.subplots(figsize=(13, 4), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.axis('off')

    bar_y = 1.8
    bar_h = 1.0
    seg_w = [3.5, 5.5, 3.5]
    seg_x = [0.5, 4.0, 9.5]
    seg_colors = [C['L3'], C['L1'], '#3d1a22']
    seg_labels = ['Trivially\nverifiable', 'Optimally\nfalsifiable', 'Non-\nfalsifiable']
    seg_examples = ['"2 + 2 = 4"', 'News claims, ad claims,\nhistorical events',
                    'Subjective opinions,\nunfalsifiable predictions']

    for x, w, color, label, ex in zip(seg_x, seg_w, seg_colors,
                                       seg_labels, seg_examples):
        ax.add_patch(FancyBboxPatch(
            (x, bar_y - bar_h / 2), w, bar_h,
            boxstyle='round,pad=0.06', fc=color, ec=C['edge'],
            lw=1.5, zorder=2))
        ax.text(x + w / 2, bar_y + 0.1, label, fontsize=9,
                fontweight='bold', color=C['text'],
                ha='center', va='center', zorder=4)
        ax.text(x + w / 2, bar_y - 0.3, ex, fontsize=7,
                fontstyle='italic', color='#999999',
                ha='center', va='center', zorder=4)

    # Bracket over center region
    bx0, bx1 = 4.0, 9.5
    bracket_y = bar_y + bar_h / 2 + 0.15
    brace_h = 0.15
    ax.plot([bx0, bx0, bx1, bx1],
            [bracket_y, bracket_y + brace_h, bracket_y + brace_h, bracket_y],
            color=C['accent'], lw=1.8, zorder=5)
    ax.text((bx0 + bx1) / 2, bracket_y + brace_h + 0.2,
            'Challenge mechanisms work here',
            fontsize=8, fontweight='bold', color=C['accent'],
            ha='center', va='bottom', zorder=5)

    # Arrows showing direction
    ax.annotate('', xy=(0.5, bar_y - bar_h / 2 - 0.3),
                xytext=(13, bar_y - bar_h / 2 - 0.3),
                arrowprops=dict(arrowstyle='<->', color=C['edge'],
                               lw=1.0, mutation_scale=12))
    ax.text(0.5, bar_y - bar_h / 2 - 0.5, 'Easy to verify',
            fontsize=7, color=C['edge'], ha='left', va='top')
    ax.text(13, bar_y - bar_h / 2 - 0.5, 'Impossible to falsify',
            fontsize=7, color=C['edge'], ha='right', va='top')

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor=C['bg'], pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 7. Confidence vs Reputation Trajectories
# ══════════════════════════════════════════════════════════
def fig7_confidence_reputation(out):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    fig.patch.set_facecolor(C['bg'])
    for ax in (ax1, ax2):
        ax.set_facecolor(C['bg'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(C['edge'])
        ax.spines['bottom'].set_color(C['edge'])
        ax.tick_params(colors=C['edge'], labelsize=8)

    # ── Left panel: Confidence (bond-time) ──
    ax1.set_title('Confidence (bond-time)', fontsize=11,
                  fontweight='bold', color=C['text'], pad=10)
    ax1.set_xlabel('Time', fontsize=9, color=C['text'])
    ax1.set_ylabel('Score', fontsize=9, color=C['text'])

    # Rising, pause during challenge, resume, then freeze at retraction
    t1 = np.linspace(0, 3, 30)     # rising
    t2 = np.linspace(3, 5, 20)     # challenged: flat
    t3 = np.linspace(5, 7.5, 25)   # resumed rising
    t4 = np.linspace(7.5, 10, 25)  # retracted: frozen

    y1 = t1 * 0.8
    y2 = np.full_like(t2, y1[-1])
    y3 = y2[-1] + (t3 - t3[0]) * 0.8
    y4 = np.full_like(t4, y3[-1])

    ax1.plot(np.concatenate([t1, t2, t3, t4]),
             np.concatenate([y1, y2, y3, y4]),
             color='#4ec9b0', lw=2.5, zorder=3)

    # Shaded regions
    ax1.axvspan(3, 5, alpha=0.18, color='#E8A040', zorder=1)
    ax1.axvspan(7.5, 10, alpha=0.18, color=C['accent'], zorder=1)

    # Annotations
    ax1.annotate('Challenged\n(paused)', xy=(4, y1[-1] + 0.3),
                 fontsize=8, color='#E8A040', ha='center', va='bottom',
                 fontweight='bold')
    ax1.annotate('Withdrawn\n(frozen)', xy=(8.75, y3[-1] + 0.3),
                 fontsize=8, color=C['accent'], ha='center', va='bottom',
                 fontweight='bold')

    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 7)
    ax1.set_xticks([])
    ax1.set_yticks([])

    # ── Right panel: Author Reputation ──
    ax2.set_title('Author Reputation', fontsize=11,
                  fontweight='bold', color=C['text'], pad=10)
    ax2.set_xlabel('Publication rounds', fontsize=9, color=C['text'])
    ax2.set_ylabel('Reputation', fontsize=9, color=C['text'])

    # Honest author: slow rise, one debunk slash at t~4.5, then recovery
    t = np.linspace(0, 10, 200)
    honest = np.zeros_like(t)
    slash_t = 4.5
    for i in range(1, len(t)):
        honest[i] = honest[i-1] + 0.055
        if abs(t[i] - slash_t) < 0.1:
            honest[i] = max(0, honest[i] - 2.0)

    # Dishonest author: repeated slashing, stays near zero
    dishonest = np.zeros_like(t)
    slash_points = [2.0, 3.8, 5.6, 7.4, 9.0]
    for i in range(1, len(t)):
        dishonest[i] = dishonest[i-1] + 0.055
        for sp in slash_points:
            if abs(t[i] - sp) < 0.1:
                dishonest[i] = max(0, dishonest[i] - 2.0)

    ax2.plot(t, honest, color='#4ec9b0', lw=2.5, label='Honest author',
             zorder=3)
    ax2.plot(t, dishonest, color=C['accent'], lw=2.0, linestyle='--',
             label='Dishonest author', zorder=3)

    # Mark the debunked event on honest line
    debunk_idx = np.argmin(np.abs(t - slash_t))
    ax2.annotate('Debunked', xy=(t[debunk_idx], honest[debunk_idx]),
                 xytext=(t[debunk_idx] - 1.5, honest[debunk_idx] + 2.0),
                 fontsize=8, color=C['accent'], fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=C['accent'], lw=1.0))

    ax2.legend(fontsize=8, loc='upper left', framealpha=0.9,
               edgecolor=C['edge'], facecolor=C['bg'],
               labelcolor=C['text'])
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 7)
    ax2.set_xticks([])
    ax2.set_yticks([])

    fig.tight_layout(w_pad=3)
    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor=C['bg'], pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 8. Pool Economics Money Flow
# ══════════════════════════════════════════════════════════
def fig8_pool_economics(out):
    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=300)
    ax.set_xlim(-0.5, 13.0)
    ax.set_ylim(-0.5, 8.5)
    ax.axis('off')

    W, H = 2.8, 0.75

    # Central: Reward Budget
    rbx, rby = 6.0, 4.5
    _box(ax, rbx, rby, 3.2, 1.0, 'Reward\nBudget',
         fs=11, fill=C['L1'], ec=C['accent'])

    # Actors
    pcx, pcy = 1.8, 7.2    # Pool Creator
    chx, chy = 10.2, 7.2   # Challenger
    cux, cuy = 1.8, 1.5    # Curators
    ddrx, ddry = 10.2, 1.5 # DDR

    _box(ax, pcx, pcy, W, H, 'Pool Creator', fs=9)
    _box(ax, chx, chy, W, H, 'Challenger', fs=9)
    _box(ax, cux, cuy, W, H, 'Curators', fs=9)
    _box(ax, ddrx, ddry, W, H, 'DDR\n(Dispute Resolution)', fs=8)

    # Pool Creator → Reward Budget (seeds)
    s = _ep(pcx, pcy, W, H, rbx, rby)
    t = _ep(rbx, rby, 3.2, 1.0, pcx, pcy)
    _arr(ax, *s, *t, 'seeds budget', lo=(-1.0, 0.3), fs=7)

    # Challenger → Reward Budget (challenge tax)
    s = _ep(chx, chy, W, H, rbx, rby)
    t = _ep(rbx, rby, 3.2, 1.0, chx, chy)
    _arr(ax, *s, *t, 'challenge tax', lo=(1.0, 0.3), fs=7)

    # Reward Budget → Curators (round rewards)
    s = _ep(rbx, rby, 3.2, 1.0, cux, cuy)
    t = _ep(cux, cuy, W, H, rbx, rby)
    _arr(ax, *s, *t, 'relevance round\nrewards', lo=(-1.3, -0.1), fs=7)

    # Challenger → DDR (counter-stake)
    s = _ep(chx, chy, W, H, ddrx, ddry)
    t = _ep(ddrx, ddry, W, H, chx, chy)
    _arr(ax, *s, *t, 'counter-stake', lo=(-1.2, 0), fs=7)

    # DDR outcomes: two annotations
    ax.text(ddrx, ddry - H / 2 - 0.45,
            'On debunk: bond to challenger\n'
            'On fail: counter-stake returned',
            fontsize=7, fontstyle='italic', color=C['text'],
            ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.2', fc=C['L2'],
                      ec=C['edge'], lw=0.8))

    # Budget depletion note
    ax.text(rbx, rby - 1.0 - 0.6,
            'If budget depletes, rounds pause;\n'
            'canonical record stays challengeable',
            fontsize=7, fontstyle='italic', color=C['accent'],
            ha='center', va='top')

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor=C['bg'], pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 9. RPGF Impact Nomination Lifecycle
# ══════════════════════════════════════════════════════════
def fig9_rpgf_impact_states(out):
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(-1.5, 13.5)
    ax.set_ylim(0, 9.5)
    ax.set_aspect('equal')
    ax.axis('off')

    W, H = 2.8, 0.75
    P = {
        'Submitted':         (3.0,  7.5),
        'Retracted':         (0.0,  5.5),
        'Unscored':          (0.0,  3.0),
        'Scored':            (6.0,  5.5),
        'Challenged':        (10.5, 5.5),
        'PendingResolution': (8.0,  3.0),
        'Disbursed':         (3.0,  1.2),
        'Debunked':          (10.5, 1.2),
    }

    terms = ('Retracted', 'Unscored', 'Disbursed', 'Debunked')
    for n, (cx, cy) in P.items():
        fs = 9 if n == 'PendingResolution' else 10
        _box(ax, cx, cy, W, H, n, term=n in terms, fs=fs)

    # ── Initial dot → Submitted ──
    ax.plot(3.0, 8.9, 'o', color=C['text'], ms=9, zorder=5)
    _arr(ax, 3.0, 8.78, 3.0, P['Submitted'][1] + H / 2 + 0.02,
         'submit nomination + post bond', lo=(1.8, 0), fs=7)

    # ── Submitted self-loop (author amends) ──
    ax.annotate('', xy=(P['Submitted'][0] - W / 2 - 0.05, P['Submitted'][1] + 0.1),
                xytext=(P['Submitted'][0] - W / 2 - 0.05, P['Submitted'][1] - 0.1),
                arrowprops=dict(arrowstyle='->', color=C['arrow'],
                               connectionstyle='arc3,rad=1.8',
                               lw=1.2, mutation_scale=14), zorder=1)
    ax.text(P['Submitted'][0] - W / 2 - 0.9, P['Submitted'][1],
            'author\namends', fontsize=6, color=C['arrow'],
            ha='right', va='center')

    # ── Submitted → Retracted ──
    s = _ep(*P['Submitted'], W, H, *P['Retracted'])
    t = _ep(*P['Retracted'], W, H, *P['Submitted'])
    _arr(ax, *s, *t, 'author retracts\n(window open)',
         lo=(-0.9, 0.3), fs=7)

    # ── Submitted → Unscored ──
    s = _ep(*P['Submitted'], W, H, *P['Unscored'])
    t = _ep(*P['Unscored'], W, H, *P['Submitted'])
    _arr(ax, *s, *t, 'quorum failure\n(twice)',
         lo=(-1.3, -0.7), fs=7)

    # ── Submitted → Scored ──
    s = _ep(*P['Submitted'], W, H, *P['Scored'])
    t = _ep(*P['Scored'], W, H, *P['Submitted'])
    _arr(ax, *s, *t, 'window closes;\nevaluation complete',
         lo=(0.3, 0.35), fs=7)

    # ── Scored → Challenged ──
    s = _ep(*P['Scored'], W, H, *P['Challenged'])
    t = _ep(*P['Challenged'], W, H, *P['Scored'])
    _arr(ax, *s, *t, 'challenge filed',
         rad=0.15, lo=(0.3, 0.35), fs=7)

    # ── Challenged → Scored ──
    _arr(ax, *t, *s, 'DDR: ChallengeFailed\n(holdback open)',
         rad=0.15, lo=(-0.3, -0.35), fs=7)

    # ── Scored → Disbursed ──
    s = _ep(*P['Scored'], W, H, *P['Disbursed'])
    t = _ep(*P['Disbursed'], W, H, *P['Scored'])
    _arr(ax, *s, *t, 'holdback expires;\nno challenge',
         lo=(-0.9, 0), fs=7)

    # ── Challenged → PendingResolution ──
    s = _ep(*P['Challenged'], W, H, *P['PendingResolution'])
    t = _ep(*P['PendingResolution'], W, H, *P['Challenged'])
    _arr(ax, *s, *t, 'holdback expires;\nchallenge pending',
         lo=(0.3, 0.4), fs=7)

    # ── Challenged → Debunked ──
    s = _ep(*P['Challenged'], W, H, *P['Debunked'])
    t = _ep(*P['Debunked'], W, H, *P['Challenged'])
    _arr(ax, *s, *t, 'DDR: Debunked',
         lo=(1.3, 0), fs=7)

    # ── PendingResolution → Disbursed ──
    s = _ep(*P['PendingResolution'], W, H, *P['Disbursed'])
    t = _ep(*P['Disbursed'], W, H, *P['PendingResolution'])
    _arr(ax, *s, *t, 'DDR: ChallengeFailed\nor timeout',
         lo=(-0.5, 0.35), fs=7)

    # ── PendingResolution → Debunked ──
    s = _ep(*P['PendingResolution'], W, H, *P['Debunked'])
    t = _ep(*P['Debunked'], W, H, *P['PendingResolution'])
    _arr(ax, *s, *t, 'DDR: Debunked',
         lo=(0.5, 0.35), fs=7)

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor=C['bg'], pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
if __name__ == '__main__':
    outdir = os.path.join(os.path.dirname(__file__))
    os.makedirs(outdir, exist_ok=True)

    figs = [
        (fig1_claim_states,        'fig-claim-states.png'),
        (fig2_actor_flow,          'fig-actor-flow.png'),
        (fig3_architecture,        'fig-architecture.png'),
        (fig4_relevance_round,     'fig-relevance-round.png'),
        (fig5_framework,           'fig-framework.png'),
        (fig6_falsifiability,      'fig-falsifiability.png'),
        (fig7_confidence_reputation, 'fig-confidence-reputation.png'),
        (fig8_pool_economics,      'fig-pool-economics.png'),
        (fig9_rpgf_impact_states,  'fig-rpgf-impact-states.png'),
    ]
    print('Generating diagrams...')
    for fn, name in figs:
        path = os.path.join(outdir, name)
        fn(path)
        print(f'  {name}')
    print('Done.')
