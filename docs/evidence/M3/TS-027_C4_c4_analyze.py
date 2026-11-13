"""TS-027 C4 offline study, stage 2: apply candidate 1 kHz -> 100 Hz filters to the recorded raw IMU and compare.

Usage: python3 c4_analyze.py <dir with rest_R1.json rest_R2.json zoh_R0_p*.json zoh_R2_p*.json> <repo>
Filters (causal; output at every raw stamp that is a multiple of 10 ms, stamped with that raw stamp):
  F0 inst   the raw sample at the output stamp (what a 100 Hz Gazebo IMU reports today)
  F1 box10  mean of the 10 raw samples in (t - 10 ms, t]   (block mean; FIR, nulls at 100, 200, ... Hz)
  F2 box20  mean of the 20 raw samples in (t - 20 ms, t]   (sliding; nulls at 50, 100, ... Hz; outputs overlap 50 %)
  F3 iir20  first-order low-pass, fc 20 Hz, run at 1 kHz, sampled at t (alpha = 1 - exp(-2 pi fc dt))
Reference: ground truth from the per-step link velocity. The D11-style window follows the TEST-M3-08 harness
(10-90 % of the speed plateau); braking uses the same rule on the descent. Statistics S1-S4 use the shared
TEST-M3_noise_stats.py (DEC-036) with the DEC-032 output sigmas.
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np

D, REPO = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location('ns', os.path.join(REPO, 'docs/evidence/M3/TEST-M3_noise_stats.py'))
ns = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ns)

FC = 20.0
ALPHA = 1 - math.exp(-2 * math.pi * FC * 0.001)
FILTERS = ['F0 inst', 'F1 box10', 'F2 box20', 'F3 iir20']
CH = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']


def load(name):
    j = json.load(open(os.path.join(D, name)))
    raw = np.array(j['raw'])
    raw = raw[np.argsort(raw[:, 0])]
    ms = np.round(raw[:, 0] * 1000).astype(int)
    keep = np.concatenate([[True], np.diff(ms) > 0])
    raw, ms = raw[keep], ms[keep]
    return j, raw, ms, np.array(j['gt'])


def run_filters(raw, ms, full=False):
    """Return {filter: (t_out, y_out[:, 6])}; full=True evaluates every raw sample (for transients)."""
    x = raw[:, 1:7]
    n = len(x)
    cs = np.vstack([np.zeros((1, 6)), np.cumsum(x, axis=0)])
    iir = np.zeros_like(x)
    acc = x[0].copy()
    for i in range(n):
        acc = acc + ALPHA * (x[i] - acc)
        iir[i] = acc
    idx = np.arange(n) if full else np.where(ms % 10 == 0)[0]
    idx = idx[idx >= 19]
    gaps = np.diff(ms)
    assert gaps.max() == 1, f'raw stamps not contiguous at 1 ms: max gap {gaps.max()} ms'
    out = {
        'F0 inst': x[idx],
        'F1 box10': (cs[idx + 1] - cs[idx + 1 - 10]) / 10,
        'F2 box20': (cs[idx + 1] - cs[idx + 1 - 20]) / 20,
        'F3 iir20': iir[idx],
    }
    return {k: (raw[idx, 0], v) for k, v in out.items()}


def lag_corr(v, k):
    v = v - v.mean()
    return float(np.dot(v[:-k], v[k:]) / np.dot(v, v))


print(f'# TS-027 C4 offline filter study (scratch). F3 alpha = {ALPHA:.6f} (fc {FC} Hz at 1 kHz); '
      f'white-noise output/raw sigma predictions: F0 1, F1 {1/math.sqrt(10):.4f}, F2 {1/math.sqrt(20):.4f}, '
      f'F3 {math.sqrt(ALPHA / (2 - ALPHA)):.4f}')

# ---------- A. rest: output noise, independence, gravity, S1-S4 ----------
for noise in ('R1', 'R2'):
    j, raw, ms, gt = load(f'rest_{noise}.json')
    sel = raw[:, 0] >= 2.0
    print(f'\n## A. rest, noise {noise} (raw sigma accel {j["sigma_raw"][0]:.6f} m/s^2, gyro {j["sigma_raw"][1]:.6f} rad/s), '
          f'{sel.sum()} raw samples after 2 s; gt max |v| {np.abs(gt[gt[:, 0] >= 2, 1]).max():.2e} m/s')
    print('# raw autocorrelation at lags 1, 2, 5, 10 ms (independent samples -> |r| ~ 1/sqrt(n) = '
          f'{1/math.sqrt(sel.sum()):.3f}):')
    for c in (0, 2, 5):
        v = raw[sel, 1 + c]
        print(f'#   {CH[c]}: ' + ', '.join(f'r{k} {lag_corr(v, k):+.3f}' for k in (1, 2, 5, 10)))
    outs = run_filters(raw[sel], ms[sel])
    for f in FILTERS:
        t, y = outs[f]
        y = y[:1000]
        line = []
        for c in range(6):
            sig = 0.01 if c < 3 else 0.001
            bias = 0.02 if c < 3 else 0.001
            e = y[:, c] - (9.8 if c == 2 else 0.0)
            checks, _ = ns.s1_s4(list(e), sig, bias, CH[c], '')
            ok = all(k for k, _ in checks)
            s = float(np.std(e, ddof=1))
            line.append(f'{CH[c]} s/sig {s/sig:.3f}{"" if ok else "*"}')
        print(f'{f:9s} n {len(y)}  az mean {y[:, 2].mean():+.5f}  ' + '  '.join(line) +
              f'  | lag-1 corr ax {lag_corr(y[:, 0], 1):+.3f}')
    print('# * = at least one of S1-S4 fails on that channel (S2 needs 0.8 <= s/sigma <= 1.2 against DEC-032 output sigma)')

# ---------- B. motion, noise-free: accuracy, ripple, latency per phase ----------
def windows(gt):
    """Speed-up and braking windows: 10-90 % of the 0.5 m/s plateau (harness rule)."""
    t, v = gt[:, 0], gt[:, 1]
    up0 = t[np.argmax(v > 0.05)]
    up1 = t[np.argmax(v > 0.45)]
    i_peak = np.argmax(v > 0.499)
    dn0 = t[i_peak + np.argmax(v[i_peak:] < 0.45)]
    dn1 = t[i_peak + np.argmax(v[i_peak:] < 0.05)]
    return (up0, up1), (dn0, dn1)


def gt_acc(gt, a, b):
    va = np.interp(a, gt[:, 0], gt[:, 1])
    vb = np.interp(b, gt[:, 0], gt[:, 1])
    return (vb - va) / (b - a)


def step_time(gt, thr=0.1, sign=1):
    a = np.diff(gt[:, 1]) / np.diff(gt[:, 0])
    i = np.argmax(sign * a > thr)
    return gt[i + 1, 0]


rows = {f: [] for f in FILTERS}
for p in range(10):
    j, raw, ms, gt = load(f'zoh_R0_p{p}.json')
    (u0, u1), (d0, d1) = windows(gt)
    a_up, a_dn = gt_acc(gt, u0, u1), gt_acc(gt, d0, d1)
    outs = run_filters(raw, ms)
    full = run_filters(raw, ms, full=True)
    t_step = step_time(gt)                 # first physical acceleration step at the ramp start
    t_cruise = (u1 + 0.3, d0 - 0.3)
    for f in FILTERS:
        t, y = outs[f]
        m_up = y[(t >= u0) & (t <= u1), 0].mean()
        m_dn = y[(t >= d0) & (t <= d1), 0].mean()
        ins = (t >= u0 + 0.05) & (t <= u1 - 0.05)
        ripple = np.abs(y[ins, 0] - 0.5).max()
        cr = (t >= t_cruise[0]) & (t <= t_cruise[1])
        tf, yf = full[f]
        k50 = np.argmax((tf >= t_step - 0.02) & (yf[:, 0] >= 0.25))
        d50 = tf[k50] - t_step
        ko = np.argmax((t >= t_step - 0.02) & (y[:, 0] >= 0.25))
        dout = t[ko] - t_step
        rows[f].append((p, m_up, a_up, m_dn, a_dn, ripple, np.abs(y[cr, 0]).max(), d50, dout))

print('\n## B. motion, noise-free (R0), 100 Hz command hold, phases 0-9 ms. Truth: speed-up and braking means from the '
      'ground-truth speed over the harness 10-90 % windows.')
print('# per filter: D11-style speed-up error % (min..max over phases), braking error %, max |out-0.5| inside the ramp '
      '(ripple / spikes), max |out| in cruise, 50 % step delay at 1 kHz evaluation (ms), first 100 Hz output >= 50 % (ms)')
for f in FILTERS:
    r = np.array(rows[f])
    eu = 100 * (r[:, 1] - r[:, 2]) / r[:, 2]
    ed = 100 * (r[:, 3] - r[:, 4]) / r[:, 4]
    print(f'{f:9s} speed-up {eu.min():+8.2f} .. {eu.max():+8.2f} %   braking {ed.min():+8.2f} .. {ed.max():+8.2f} %   '
          f'ripple max {r[:, 5].max():6.3f} m/s^2   cruise max {r[:, 6].max():6.3f}   '
          f'd50 {1000 * r[:, 7].min():5.1f} .. {1000 * r[:, 7].max():5.1f} ms   first output {1000 * r[:, 8].min():5.1f} .. {1000 * r[:, 8].max():5.1f} ms')
print('# truth values (phase 0): speed-up %+.4f, braking %+.4f m/s^2' % (rows['F1 box10'][0][2], rows['F1 box10'][0][4]))

# F1 equals the 10 ms mean physical acceleration (Delta v / 10 ms) exactly?
j, raw, ms, gt = load('zoh_R0_p3.json')
t, y = run_filters(raw, ms)['F1 box10']
vt = np.interp(t, gt[:, 0], gt[:, 1])
vtm = np.interp(t - 0.010, gt[:, 0], gt[:, 1])
res = y[:, 0] - (vt - vtm) / 0.010
mv = (t > 0.4) & (t < 3.4)
print(f'# F1 vs ground-truth (v(t) - v(t-10 ms)) / 10 ms, phase 3, 0.4-3.4 s: max |residual| {np.abs(res[mv]).max():.2e} m/s^2 '
      f'(F1 output = mean physical acceleration of the last 10 ms; nominal group delay 4.5 ms + up to 1 step)')

# gyro: rotation leg (gt wz plateau 0.5 rad/s), D10-style mean and transient
print('\n## C. gyro z, rotation leg (noise-free R0, phases 0-9): mean over the plateau vs ground truth; max |out - truth| in the plateau')
for f in FILTERS:
    errs, devs = [], []
    for p in range(10):
        j, raw, ms, gt = load(f'zoh_R0_p{p}.json')
        t, y = run_filters(raw, ms)[f]
        pl = gt[(gt[:, 2] > 0.499)]
        a, b = pl[0, 0] + 0.05, pl[-1, 0] - 0.05
        sel = (t >= a) & (t <= b)
        g = gt[(gt[:, 0] >= a) & (gt[:, 0] <= b), 2].mean()
        errs.append(100 * (y[sel, 5].mean() - g) / g)
        devs.append(np.abs(y[sel, 5] - g).max())
    print(f'{f:9s} gyro z error {min(errs):+.4f} .. {max(errs):+.4f} %   max |dev| {max(devs):.5f} rad/s')

# ---------- D. motion with noise R2: D11 distribution over phases ----------
print('\n## D. motion with raw noise R2 (sqrt(10)-scaled), phases 0-9: D11-style speed-up and braking error %')
for f in FILTERS:
    eu, ed, cru = [], [], []
    for p in range(10):
        j, raw, ms, gt = load(f'zoh_R2_p{p}.json')
        (u0, u1), (d0, d1) = windows(gt)
        t, y = run_filters(raw, ms)[f]
        a_up, a_dn = gt_acc(gt, u0, u1), gt_acc(gt, d0, d1)
        eu.append(100 * (y[(t >= u0) & (t <= u1), 0].mean() - a_up) / a_up)
        ed.append(100 * (y[(t >= d0) & (t <= d1), 0].mean() - a_dn) / a_dn)
        cr = (t >= u1 + 0.3) & (t <= d0 - 0.3)
        cru.append(y[cr, 0].std(ddof=1))
    print(f'{f:9s} speed-up {min(eu):+8.2f} .. {max(eu):+8.2f} %  (D11 limit +-20 %: {"PASS" if max(map(abs, eu)) <= 20 else "FAIL"} in all phases'
          f'{"" if max(map(abs, eu)) <= 20 else " NOT"})   braking {min(ed):+8.2f} .. {max(ed):+8.2f} %   cruise ax s {min(cru):.4f} .. {max(cru):.4f} m/s^2')

# ---------- E. M4-relevant: velocity from integrating the 100 Hz output (dt 10 ms) vs ground truth ----------
print('\n## E. integrated forward velocity sum(out * 10 ms) vs ground-truth speed, 0.4-2.95 s (speed-up, cruise, braking; '
      'stops before the ground-truth stale point at rest); and the step response at the ramp start (outputs to reach 95 %)')
for noise in ('R0', 'R2'):
    for f in FILTERS:
        errs, n95 = [], []
        for p in range(10):
            j, raw, ms, gt = load(f'zoh_{noise}_p{p}.json')
            t, y = run_filters(raw, ms)[f]
            sel = (t >= 0.4) & (t <= 2.95)
            v_int = np.cumsum(y[sel, 0]) * 0.010
            v_gt = np.interp(t[sel], gt[:, 0], gt[:, 1]) - np.interp(0.4, gt[:, 0], gt[:, 1])
            errs.append(np.abs(v_int - v_gt).max())
            if noise == 'R0':
                ts = step_time(gt)
                k = np.argmax((t > ts) & (y[:, 0] >= 0.475))
                n95.append(int(round((t[k] - ts) * 1000)))
        extra = f'   first output >= 95 % of 0.5 m/s^2: {min(n95)} .. {max(n95)} ms after the first physical step' if n95 else ''
        print(f'{noise} {f:9s} max |v_int - v_gt| {min(errs):.4f} .. {max(errs):.4f} m/s over phases{extra}')
