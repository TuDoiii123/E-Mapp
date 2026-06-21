from services.queue_lstm import build_series, make_windows, scale, unscale


def test_build_series_sorted():
    rows = [('2026-06-02', 9, 5), ('2026-06-01', 8, 3), ('2026-06-01', 9, 7)]
    assert build_series(rows) == [3.0, 7.0, 5.0]


def test_make_windows_shapes():
    series = [1.0, 2.0, 3.0, 4.0, 5.0]
    X, y = make_windows(series, lookback=2)
    assert X == [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]]
    assert y == [3.0, 4.0, 5.0]


def test_make_windows_too_short():
    assert make_windows([1.0, 2.0], lookback=5) == ([], [])


def test_scale_unscale_invertible():
    series = [0.0, 5.0, 10.0]
    scaled, mn, mx = scale(series)
    assert scaled == [0.0, 0.5, 1.0]
    assert abs(unscale(scaled[1], mn, mx) - 5.0) < 1e-9


def test_scale_constant_series():
    scaled, mn, mx = scale([4.0, 4.0, 4.0])
    assert all(s == 0.0 for s in scaled)
    assert unscale(0.0, mn, mx) == 4.0
