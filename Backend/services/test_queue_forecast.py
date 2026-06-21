from services.queue_forecast import (
    synth_count, weekday_hour_avg, percentiles, load_level,
)


def test_synth_count_patterns():
    assert synth_count(20, 0, 9) > synth_count(20, 6, 9)
    assert synth_count(20, 0, 9) > synth_count(20, 0, 12)
    assert synth_count(20, 0, 20) == 0
    assert synth_count(20, 0, 6) == 0
    assert synth_count(5, 6, 13) >= 0


def test_weekday_hour_avg():
    rows = [(0, 9, 10.0), (0, 9, 20.0), (0, 10, 5.0), (1, 9, 8.0)]
    avg = weekday_hour_avg(rows)
    assert avg[(0, 9)] == 15.0
    assert avg[(0, 10)] == 5.0
    assert avg[(1, 9)] == 8.0


def test_percentiles_and_load_level():
    vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    p50, p85 = percentiles(vals)
    assert 5 <= p50 <= 6
    assert 8 <= p85 <= 9.5
    assert load_level(1, p50, p85) == 'low'
    assert load_level(p50 + 0.1, p50, p85) == 'medium'
    assert load_level(p85 + 1, p50, p85) == 'high'


def test_percentiles_empty():
    assert percentiles([]) == (0.0, 0.0)
