"""Test chuẩn hóa text cho TTS. Chạy: python -m ai_voice_backend.test_text_normalizer"""
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')  # console Windows cp1252 → ép UTF-8
from ai_voice_backend.text_normalizer import number_to_words, normalize, to_ssml


def _check(actual, expected, label):
    status = 'OK ' if actual == expected else 'FAIL'
    if actual != expected:
        print(f'[{status}] {label}\n        got: {actual!r}\n        exp: {expected!r}')
    else:
        print(f'[{status}] {label}')
    return actual == expected


def main() -> int:
    ok = True

    # Số → chữ
    ok &= _check(number_to_words(0), 'không', 'số 0')
    ok &= _check(number_to_words(5), 'năm', 'số 5')
    ok &= _check(number_to_words(15), 'mười lăm', 'số 15')
    ok &= _check(number_to_words(21), 'hai mươi mốt', 'số 21')
    ok &= _check(number_to_words(24), 'hai mươi tư', 'số 24')
    ok &= _check(number_to_words(105), 'một trăm linh năm', 'số 105')
    ok &= _check(number_to_words(2026), 'hai nghìn không trăm hai mươi sáu', 'năm 2026')
    ok &= _check(number_to_words(1000), 'một nghìn', 'số 1000')
    ok &= _check(number_to_words(1234567), 'một triệu hai trăm ba mươi tư nghìn năm trăm sáu mươi bảy', 'số 1.234.567')

    # Giờ
    ok &= _check(normalize('09:00'), 'chín giờ', 'giờ 09:00')
    ok &= _check(normalize('14:30'), 'mười bốn giờ rưỡi', 'giờ 14:30')
    ok &= _check(normalize('08:15'), 'tám giờ mười lăm phút', 'giờ 08:15')

    # Ngày
    ok &= _check(normalize('01/07/2026'),
                 'ngày mùng một tháng bảy năm hai nghìn không trăm hai mươi sáu', 'ngày 01/07/2026')
    ok &= _check(normalize('25/12/2026'),
                 'ngày hai mươi lăm tháng mười hai năm hai nghìn không trăm hai mươi sáu', 'ngày 25/12/2026')

    # Viết tắt
    ok &= _check(normalize('làm CCCD'), 'làm căn cước công dân', 'viết tắt CCCD')
    ok &= _check(normalize('nộp tại UBND'), 'nộp tại Ủy ban nhân dân', 'viết tắt UBND')

    # Câu thực tế từ dialog_manager
    out = normalize('Ngày 01/07/2026 tại UBND còn trống các khung giờ: 08:00, 09:00.')
    print(f'[câu thật] {out}')

    out2 = normalize('• Giờ: 09:00\n• Ngày: 01/07/2026')
    print(f'[bullet]   {out2}')

    # SSML hợp lệ
    ssml = to_ssml(normalize('Xin chào. Bạn cần gì?'))
    ok &= _check(ssml.startswith('<speak>') and ssml.endswith('</speak>'), True, 'SSML bọc <speak>')
    print(f'[ssml]     {ssml}')

    print('\n' + ('=== TẤT CẢ PASS ===' if ok else '=== CÓ TEST FAIL ==='))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
