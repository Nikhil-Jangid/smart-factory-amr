"""DEC-036 statistical noise checks S1-S4 (sensors.md §7.4), shared by Task C (TEST-M3-05) and Task D (TEST-M3-07).

Written once before the two tasks started (2026-11-03) and imported by both, so that the same statistic is
computed the same way for the LiDAR and the IMU. Errors e_i = sample - expected (sensors.md §7.2).
  S1  bias |mean(e)| <= bias_limit (per channel, given by the caller from sensors.md §7.4)
  S2  0.8 <= s / sigma_config <= 1.2 (s = sample standard deviation, n - 1)
  S3  fraction of samples with |e_i - mean| <= 2 s in [0.93, 0.98]
  S4  0 samples with |e_i - mean| > 6 sigma_config
"""
import math


def s1_s4(errors, sigma_config, bias_limit, label, unit):
    """Return a list of (ok, text) for S1-S4 on `errors`; also the summary line (n, mean, s, min, max)."""
    n = len(errors)
    if n < 2:
        return [(False, f'{label}: only {n} samples')], f'{label}: n = {n}'
    mean = sum(errors) / n
    s = math.sqrt(sum((e - mean) ** 2 for e in errors) / (n - 1))
    within = sum(abs(e - mean) <= 2 * s for e in errors) / n
    outliers = sum(abs(e - mean) > 6 * sigma_config for e in errors)
    ratio = s / sigma_config
    summary = (f'{label}: n = {n}, mean error {mean:+.6f} {unit}, s {s:.6f} {unit}, '
               f'min {min(errors):+.6f}, max {max(errors):+.6f} {unit}')
    checks = [
        (abs(mean) <= bias_limit, f'S1 {label}: |mean error| {abs(mean):.6f} {unit} <= {bias_limit} {unit}'),
        (0.8 <= ratio <= 1.2, f'S2 {label}: s / sigma = {s:.6f} / {sigma_config} = {ratio:.4f} in [0.8, 1.2]'),
        (0.93 <= within <= 0.98, f'S3 {label}: fraction within 2 s = {within:.4f} in [0.93, 0.98]'),
        (outliers == 0, f'S4 {label}: {outliers} samples beyond 6 sigma ({6 * sigma_config:g} {unit}) == 0'),
    ]
    return checks, summary
