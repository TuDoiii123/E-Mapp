"""Test trích ngày tiếng Việt (regex fallback) + phân loại lỗi rate-limit."""
from datetime import date

from ai_voice_backend.nlu import (
    NLUEngine, _extract_date_vi, _is_rate_limit_error,
)

_TODAY = date(2026, 6, 16)


def test_explicit_full_vietnamese_date():
    assert _extract_date_vi('ngày 1 tháng 7 năm 2026', _TODAY) == '2026-07-01'
    assert _extract_date_vi('mùng 5 tháng 7 năm 2026', _TODAY) == '2026-07-05'
    assert _extract_date_vi('mồng 10 tháng 12 năm 2026', _TODAY) == '2026-12-10'


def test_numeric_dates():
    assert _extract_date_vi('1/7/2026', _TODAY) == '2026-07-01'
    assert _extract_date_vi('01-07-2026', _TODAY) == '2026-07-01'
    assert _extract_date_vi('2026-07-01', _TODAY) == '2026-07-01'


def test_thang_without_year_picks_future():
    # 16/6/2026 là hôm nay → 'ngày 5 tháng 7' cùng năm (tương lai)
    assert _extract_date_vi('ngày 5 tháng 7', _TODAY) == '2026-07-05'
    # tháng đã qua → sang năm sau
    assert _extract_date_vi('ngày 5 tháng 1', _TODAY) == '2027-01-05'


def test_relative_dates():
    assert _extract_date_vi('hôm nay', _TODAY) == '2026-06-16'
    assert _extract_date_vi('đặt lịch ngày mai nhé', _TODAY) == '2026-06-17'
    assert _extract_date_vi('ngày kia', _TODAY) == '2026-06-18'


def test_invalid_or_absent():
    assert _extract_date_vi('không có ngày gì', _TODAY) is None
    assert _extract_date_vi('ngày 32 tháng 13 năm 2026', _TODAY) is None
    assert _extract_date_vi('', _TODAY) is None


def test_regex_fallback_uses_vietnamese_date():
    eng = NLUEngine()
    r = eng._regex_fallback('làm căn cước ngày 1 tháng 7 năm 2026')
    assert r.entities.appointment_date == '2026-07-01'


def test_rate_limit_classifier():
    assert _is_rate_limit_error('429 You exceeded your current quota')
    assert _is_rate_limit_error('ResourceExhausted: quota exceeded')
    assert _is_rate_limit_error('Rate limit reached')
    assert not _is_rate_limit_error('400 invalid argument')
    assert not _is_rate_limit_error('')
