#!/usr/bin/env python3
"""
Figure 2 — PNAS Brief Report.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def complex_mult(a_re, a_im, b_re, b_im):
    return (a_re * b_re - a_im * b_im, a_re * b_im + a_im * b_re)

def run_outward(num_steps, rng):
    traj = [{"x": 0.0, "y": 0.0, "I_re": 1.0, "I_im": 0.0}]
    z1_re, z1_im = 1.0, 1.0
    for _ in range(num_steps):
        prev = traj[-1]
        if rng.random() < 0.5: i_n_re, i_n_im = 0.0, 1.0
        else: i_n_re, i_n_im = 0.0, -1.0
        newI_re, newI_im = complex_mult(prev["I_re"], prev["I_im"], i_n_re, i_n_im)
        if i_n_im == 1.0:
            zd_re = 0.5 + rng.random() * 0.5; zd_im = rng.random() * 0.5
        else:
            zd_re = rng.random() * 0.5; zd_im = 0.5 + rng.random() * 0.5
        Iz1_re, Iz1_im = complex_mult(newI_re, newI_im, z1_re, z1_im)
        traj.append({"x": prev["x"] + Iz1_im + zd_im, "y": prev["y"] + Iz1_re + zd_re,
                      "I_re": newI_re, "I_im": newI_im})
    return traj

def run_return(traj, rng):
    last = traj[-1]
    X_n, Y_n = last["x"], last["y"]
    path = []
    for _ in range(10000):
        if X_n + Y_n < 1.0: break
        prevX, prevY = X_n, Y_n
        epsilon = -0.5 + rng.random()
        denom = prevX + prevY
        if abs(denom) > 0.001:
            X_n = prevX - (prevX / denom) + epsilon
            Y_n = prevY - (prevY / denom) + epsilon
        else: break
        path.append((X_n, Y_n))
    path.append((0.0, 0.0))
    return path

def compute_ae(traj, ret):
    xs = np.array([p["x"] for p in traj])
    ys = np.array([p["y"] for p in traj])
    ideal = np.arctan2(-ys[-1], -xs[-1])
    if len(ret) > 1:
        dx, dy = ret[0][0] - xs[-1], ret[0][1] - ys[-1]
        ae = np.degrees(np.arctan2(dy, dx) - ideal)
        ae = ((ae + 180) % 360) - 180
        return abs(ae)
    return np.nan

# Panel B: seed=9798, 100 steps
rng = np.random.default_rng(9798)
traj = run_outward(100, rng)
ret = run_return(traj, rng)
xs_out = np.array([p["x"] for p in traj])
ys_out = np.array([p["y"] for p in traj])
ret_xs = [xs_out[-1]] + [p[0] for p in ret]
ret_ys = [ys_out[-1]] + [p[1] for p in ret]

# Panel C: n=1000
rng_c = np.random.default_rng(42)
all_ae = []
for _ in range(1000):
    t = run_outward(20, rng_c); r = run_return(t, rng_c)
    ae = compute_ae(t, r)
    if not np.isnan(ae): all_ae.append(ae)
med_ae = np.median(all_ae); mean_ae = np.mean(all_ae)
print(f"Panel C: median={med_ae:.1f}, mean={mean_ae:.1f}")

# ═══ FIGURE ═══
fig = plt.figure(figsize=(7.5, 9))
gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1], hspace=0.35, wspace=0.35)

# Panel B (Panel A is the ant figure - added in Illustrator)
ax_b = fig.add_subplot(gs[0, 1])
ax_b.plot(xs_out, ys_out, color='black', linewidth=0.4, solid_capstyle='round', zorder=2)
ax_b.plot(ret_xs, ret_ys, color='black', linewidth=0.6, linestyle=(0, (2, 2)), zorder=3)
ax_b.plot(0, 0, 'ks', markersize=4, zorder=5)
ax_b.plot(xs_out[-1], ys_out[-1], 'ko', markersize=4, zorder=5)
ax_b.set_aspect('equal')
ax_b.axis('off')

# Panel A placeholder - empty with dashed border
ax_a = fig.add_subplot(gs[0, 0])
ax_a.set_xlim(0, 1); ax_a.set_ylim(0, 1)
for spine in ax_a.spines.values(): spine.set_linestyle('--'); spine.set_color('#aaa')
ax_a.set_xticks([]); ax_a.set_yticks([])

# Panel C - histogram only, no text
ax_c = fig.add_subplot(gs[1, 0])
ax_c.hist(all_ae, bins=40, color='#888888', edgecolor='white',
          linewidth=0.3, alpha=0.85, zorder=2)
ax_c.axvline(med_ae, color='black', linewidth=1.2, linestyle='-', zorder=4)
ax_c.axvline(mean_ae, color='black', linewidth=1.2, linestyle='--', zorder=4)

# Cross-species bracket (no text label)
y_pos = 310 * 0.68
ax_c.plot([10, 25], [y_pos, y_pos], 'k-', linewidth=1.2, zorder=5)
ax_c.plot([10, 10], [y_pos - 7, y_pos + 7], 'k-', linewidth=0.9, zorder=5)
ax_c.plot([25, 25], [y_pos - 7, y_pos + 7], 'k-', linewidth=0.9, zorder=5)

ax_c.set_xlim(0, 75)
ax_c.set_ylim(0, 320)
ax_c.set_xticklabels([])
ax_c.set_yticklabels([])
ax_c.spines['top'].set_visible(False); ax_c.spines['right'].set_visible(False)

# Panel D - bars only, no text
ax_d = fig.add_subplot(gs[1, 1])
models = ['', '', '']
arith_ops = [10, 5, 5]
trig_cost = [0, 24, 48]
x = np.arange(len(models))
width = 0.30
ax_d.bar(x - width/2, arith_ops, width, color='black', zorder=2)
ax_d.bar(x + width/2, trig_cost, width, color='#aaaaaa', zorder=2)
ax_d.set_xticks(x)
ax_d.set_xticklabels(models)
ax_d.set_yticklabels([])
ax_d.set_ylim(0, 55)
ax_d.spines['top'].set_visible(False); ax_d.spines['right'].set_visible(False)

plt.savefig('figure2_notext.png', dpi=600, bbox_inches='tight', facecolor='white')
plt.savefig('figure2_notext.tiff', dpi=600, bbox_inches='tight', facecolor='white')
print("Saved: figure2_notext.png / .tiff (600 DPI, no text)")
