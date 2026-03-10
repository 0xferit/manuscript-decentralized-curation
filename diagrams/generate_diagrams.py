#!/usr/bin/env python3
"""Generate conceptual diagrams for the Truth Post paper.

Produces:
  diagrams/fig-claim-states.png    Claim state machine
  diagrams/fig-actor-flow.png      Actor interaction flow
  diagrams/fig-architecture.png    Protocol architecture layers
  diagrams/fig-relevance-round.png Relevance round sequence
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

# ── Colors ──
C = dict(
    text='#2D2D2D', box='#E4EBF2', edge='#6B7D8E',
    term='#C8CFD8', term_e='#4A5568', accent='#3D6098',
    arrow='#4A5568', L1='#D6E4F0', L2='#E8E0D0', L3='#D6E8D6',
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
                bbox=dict(boxstyle='round,pad=0.12', fc='white',
                          ec='none', alpha=0.9))


# ══════════════════════════════════════════════════════════
# 1. Claim State Machine
# ══════════════════════════════════════════════════════════
def fig1_claim_states(out):
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    ax.axis('off')

    W, H = 2.4, 0.75
    P = {
        'Live':           (5.0, 6.0),
        'Challenged':     (8.2, 3.8),
        'RetractPending': (1.8, 3.8),
        'Retracted':      (1.8, 1.4),
        'Debunked':       (8.2, 1.4),
    }

    for n, (cx, cy) in P.items():
        _box(ax, cx, cy, W, H, n, term=n in ('Retracted', 'Debunked'))

    # ── Initial dot → Live ──
    ax.plot(5, 7.4, 'o', color=C['text'], ms=9, zorder=5)
    _arr(ax, 5, 7.28, 5, P['Live'][1] + H / 2 + 0.02,
         'post claim + lock bond', lo=(1.5, 0))

    # ── Live → Challenged ──
    s = _ep(*P['Live'], W, H, *P['Challenged'])
    t = _ep(*P['Challenged'], W, H, *P['Live'])
    _arr(ax, *s, *t, 'challenge filed\n(confidence paused)',
         rad=0.2, lo=(0.3, 0.35))

    # ── Challenged → Live ──
    _arr(ax, *t, *s, 'challenge fails\n(confidence resumes)',
         rad=0.2, lo=(-0.3, -0.35))

    # ── Challenged → Debunked ──
    s = _ep(*P['Challenged'], W, H, *P['Debunked'])
    t = _ep(*P['Debunked'], W, H, *P['Challenged'])
    _arr(ax, *s, *t, 'challenge succeeds\n(bond transferred)',
         lo=(1.6, 0))

    # ── Live → RetractPending ──
    s = _ep(*P['Live'], W, H, *P['RetractPending'])
    t = _ep(*P['RetractPending'], W, H, *P['Live'])
    _arr(ax, *s, *t, 'author initiates\nretraction',
         rad=-0.2, lo=(-0.3, 0.35))

    # ── RetractPending → Challenged ──
    s = _ep(*P['RetractPending'], W, H, *P['Challenged'])
    t = _ep(*P['Challenged'], W, H, *P['RetractPending'])
    _arr(ax, *s, *t, 'challenge during cooldown', lo=(0, 0.3))

    # ── RetractPending → Retracted ──
    s = _ep(*P['RetractPending'], W, H, *P['Retracted'])
    t = _ep(*P['Retracted'], W, H, *P['RetractPending'])
    _arr(ax, *s, *t, 'cooldown expires\n(confidence frozen)',
         lo=(-1.5, 0))

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor='white', pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 2. Actor Interaction Flow
# ══════════════════════════════════════════════════════════
def fig2_actor_flow(out):
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-0.5, 7.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # Central protocol column
    pw, ph = 3.0, 5.5
    pcx, pcy = 5.5, 3.5
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
        _box(ax, pcx, sy, 2.6, 0.55, s, fs=9, bold=False,
             fill='white', ec=C['edge'])

    # Left-side actors
    AW, AH = 2.0, 0.65
    left_actors = [
        ('Authors',       6.2),
        ('Challengers',   4.5),
        ('Curators',      2.8),
        ('Pool Creators', 1.1),
    ]
    for name, y in left_actors:
        _box(ax, 1.3, y, AW, AH, name, fs=9)

    # Right-side actors
    right_actors = [
        ('Jurors (DDR)',          5.5),
        ('Interface\nOperators', 2.0),
    ]
    for name, y in right_actors:
        _box(ax, 10.0, y, AW, AH, name, fs=9)

    # Arrows: left actors → protocol
    left_flows = [
        (6.2, 5.7, 'post claims\n+ bonds'),
        (4.5, 4.0, 'file challenges\n+ counter-stake'),
        (2.8, 2.5, 'stake +\ncommit/reveal'),
        (1.1, 1.3, 'define pool\nconfig'),
    ]
    for ay, py, lbl in left_flows:
        _arr(ax, 1.3 + AW / 2, ay, pcx - pw / 2, py,
             lbl, lo=(0, 0.32), fs=7)

    # Arrows: protocol ↔ jurors
    _arr(ax, pcx + pw / 2, 5.2, 10.0 - AW / 2, 5.7,
         'disputes', lo=(0, 0.22), fs=7)
    _arr(ax, 10.0 - AW / 2, 5.3, pcx + pw / 2, 4.6,
         'verdicts', lo=(0, -0.22), fs=7)

    # Arrow: protocol → interface operators
    _arr(ax, pcx + pw / 2, 2.0, 10.0 - AW / 2, 2.0,
         'read canonical state,\nrender feeds', lo=(0, 0.32), fs=7)

    # Annotation
    ax.text(pcx, pcy - ph / 2 - 0.35,
            'challenge tax \u2192 pool reward budget',
            fontsize=8, fontstyle='italic', color=C['accent'],
            ha='center', va='top')

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor='white', pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 3. Protocol Architecture Layers
# ══════════════════════════════════════════════════════════
def fig3_architecture(out):
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 8)
    ax.set_aspect('equal')
    ax.axis('off')

    layers = [
        ('Interfaces  (replaceable)',
         4.2, C['L3'],
         'Any frontend: feeds, dashboards, dispute history, pool browsers'),
        ('Content & Indexing  (off-chain, reconstructible)',
         2.2, C['L2'],
         'Claim blobs, evidence bundles, policy documents, indexers'),
        ('Canonical Protocol State  (on-chain)',
         0.2, C['L1'],
         'Pools, claim refs, stakes, challenges, adjudication links, '
         'confidence, payouts'),
    ]

    lw_box, lh_box = 8.0, 1.4
    lx = 1.0
    for title, cy, color, desc in layers:
        ax.add_patch(FancyBboxPatch(
            (lx, cy - lh_box / 2), lw_box, lh_box,
            boxstyle='round,pad=0.1', fc=color, ec=C['edge'],
            lw=1.5, zorder=2))
        ax.text(lx + 0.3, cy + 0.25, title, fontsize=10,
                fontweight='bold', color=C['text'], va='center', zorder=4)
        ax.text(lx + 0.3, cy - 0.25, desc, fontsize=8,
                fontstyle='italic', color='#555555', va='center', zorder=4)

    # Inter-layer arrows
    mid_x = lx + lw_box / 2
    _arr(ax, mid_x, 4.2 - lh_box / 2, mid_x, 2.2 + lh_box / 2)
    _arr(ax, mid_x, 2.2 - lh_box / 2, mid_x, 0.2 + lh_box / 2)

    # Architectural commitments (top left)
    ax.text(1.0, 7.4, 'Architectural commitments', fontsize=10,
            fontweight='bold', color=C['accent'])
    for i, c in enumerate([
        'Permissionless pools',
        'Immutable contracts',
        'Minimal governance',
    ]):
        ax.text(1.3, 7.0 - i * 0.35, '\u2022  ' + c, fontsize=9,
                color=C['text'])

    # Pool economics (top right)
    ax.text(5.5, 7.4, 'Pool economics', fontsize=10,
            fontweight='bold', color=C['accent'])
    for i, c in enumerate([
        'Local reward budgets',
        'Challenge tax \u2192 pool budget',
        'No global treasury',
    ]):
        ax.text(5.8, 7.0 - i * 0.35, '\u2022  ' + c, fontsize=9,
                color=C['text'])

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor='white', pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
# 4. Relevance Round Sequence
# ══════════════════════════════════════════════════════════
def fig4_relevance_round(out):
    fig, ax = plt.subplots(figsize=(7, 10), dpi=300)
    ax.set_xlim(0, 7)
    ax.set_ylim(-0.5, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    steps = [
        ('1', 'Curators stake into pool'),
        ('2', 'Round scheduled for Live item\nat pool-defined cadence'),
        ('3', r'Stake-weighted draft:  $d_i = s_i$'),
        ('4', 'Drafted curators commit/reveal\nscores in [0, 1]'),
        ('5', r'Weight capping:'
              '\n'
              r'$w_i = \min(s_i,\; c \cdot \mathrm{total\_stake})$'),
        ('6', r'Coherence check:'
              '\n'
              r'slash if $|v_i - \mu| > K\sigma$'),
        ('7', 'Near-flat rounds cancelled\nas degenerate'),
    ]

    cx = 3.8
    bw, bh = 5.0, 0.85
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

        _box(ax, cx, cy, bw, bh, text, fs=9, bold=False)

        # Arrow to next step
        if i < len(steps) - 1:
            _arr(ax, cx, cy - bh / 2, cx, cy - gap + bh / 2)

    fig.savefig(out, dpi=300, bbox_inches='tight',
                facecolor='white', pad_inches=0.3)
    plt.close(fig)


# ══════════════════════════════════════════════════════════
if __name__ == '__main__':
    outdir = os.path.join(os.path.dirname(__file__))
    os.makedirs(outdir, exist_ok=True)

    figs = [
        (fig1_claim_states,   'fig-claim-states.png'),
        (fig2_actor_flow,     'fig-actor-flow.png'),
        (fig3_architecture,   'fig-architecture.png'),
        (fig4_relevance_round, 'fig-relevance-round.png'),
    ]
    print('Generating diagrams...')
    for fn, name in figs:
        path = os.path.join(outdir, name)
        fn(path)
        print(f'  {name}')
    print('Done.')
