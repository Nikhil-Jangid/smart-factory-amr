#!/usr/bin/env python3
"""OPEN-09 probe: how the installed Gazebo Sim / DART combines surface friction coefficients.
Usage: python3 -I OPEN-09_friction_probe.py <world.sdf>   (run with a unique GZ_PARTITION)
Gravity is tilted so tan(theta) = 0.4 on a flat ground plane with mu = 0.6; boxes start at rest.
Sliding acceleration along +x: a = g sin(theta) - mu_eff g cos(theta) (if positive), else 0."""
import math, re, subprocess, sys, os, signal
world = sys.argv[1]
srv = subprocess.Popen(['gz', 'sim', '-s', '-r', world], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, start_new_session=True)
def sample():
    out = subprocess.run(['gz', 'topic', '-e', '-t', '/world/probe/pose/info', '-n', '1'], capture_output=True, text=True, timeout=30).stdout
    m = re.search(r'stamp \{(.*?)\}', out, re.S)  # protobuf text omits zero fields (sec or nsec)
    sec = re.search(r'sec: (\d+)', re.sub(r'nsec: \d+', '', m.group(1))) if m else None
    nsec = re.search(r'nsec: (\d+)', m.group(1)) if m else None
    t = (int(sec.group(1)) if sec else 0) + (int(nsec.group(1)) * 1e-9 if nsec else 0.0) if m else float('nan')
    poses = {}
    for blk in re.finditer(r'pose \{\s*name: "(box_[a-z0-9]+)".*?position \{(.*?)\}', out, re.S):
        xm = re.search(r'x: ([-\d.e]+)', blk.group(2))
        poses[blk.group(1)] = float(xm.group(1)) if xm else 0.0
    return t, poses
try:
    samples = []
    while True:
        t, p = sample()
        if p and (not samples or t >= samples[-1][0] + 0.5):
            samples.append((t, p))
        if t >= 3.0:
            break
finally:
    os.killpg(srv.pid, signal.SIGINT); srv.wait(timeout=20)
th = math.atan(0.4); g = 9.81
print(f'# world {os.path.basename(world)}; theta {math.degrees(th):.3f} deg; ground mu 0.6; g sin {g*math.sin(th):.4f}, g cos {g*math.cos(th):.4f} m/s^2')
t0, p0 = samples[0]; t1, p1 = samples[-1]
print(f'# samples at sim t = {t0:.3f} s and {t1:.3f} s ({len(samples)} reads)')
print(f"{'box':12} {'x0 [m]':>10} {'x1 [m]':>10} {'a_meas':>8} | predicted a [m/s^2] for mu_eff = min / product / max")
for name, mu in [('box_mu000',0.0),('box_mu001',0.01),('box_mu030',0.3),('box_mu050',0.5),('box_mu100',1.0),('box_default',1.0)]:
    x0, x1 = p0.get(name, float('nan')), p1.get(name, float('nan'))
    # x(t) = x(0) + a t^2 / 2 from rest at t = 0; x(0) = 0 for every box
    a = 2 * (x1 - x0) / (t1**2 - t0**2) if t1 > t0 else float('nan')
    pred = [max(0.0, g*math.sin(th) - me*g*math.cos(th)) for me in (min(mu,0.6), mu*0.6, max(mu,0.6))]
    print(f'{name:12} {x0:10.5f} {x1:10.5f} {a:8.4f} | ' + ' / '.join(f'{v:.4f}' for v in pred))
print('# server stderr (tail):'); print('\n'.join(srv.stderr.read().decode(errors='replace').splitlines()[-5:]))
