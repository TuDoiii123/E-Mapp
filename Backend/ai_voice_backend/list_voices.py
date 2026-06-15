"""
Liệt kê các giọng TTS tiếng Việt (vi-VN) mà tài khoản Google Cloud của bạn
truy cập được — để biết đặt GOOGLE_TTS_VOICE_NAME thành giá trị nào.

Yêu cầu:
    - Đã cài: pip install google-cloud-texttospeech
    - Đã set: GOOGLE_APPLICATION_CREDENTIALS=đường_dẫn_key.json

Chạy:
    python -m ai_voice_backend.list_voices
    python -m ai_voice_backend.list_voices --all     # tất cả ngôn ngữ
"""
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')  # console Windows cp1252 → ép UTF-8


def main() -> int:
    show_all = '--all' in sys.argv
    lang_prefix = '' if show_all else 'vi-VN'

    try:
        from google.cloud import texttospeech as tts
    except ImportError:
        print('[LỖI] Chưa cài google-cloud-texttospeech.')
        print('      Chạy: pip install google-cloud-texttospeech')
        return 1

    try:
        client = tts.TextToSpeechClient()
        voices = client.list_voices().voices
    except Exception as e:  # noqa: BLE001
        print(f'[LỖI] Không gọi được ListVoices: {e}')
        print('      Kiểm tra GOOGLE_APPLICATION_CREDENTIALS đã trỏ đúng key.json chưa.')
        return 1

    rows = []
    for v in voices:
        if lang_prefix and not any(c.startswith(lang_prefix) for c in v.language_codes):
            continue
        gender = tts.SsmlVoiceGender(v.ssml_gender).name
        rows.append((v.name, gender, v.natural_sample_rate_hertz))

    rows.sort()
    if not rows:
        print(f'Không tìm thấy giọng nào cho "{lang_prefix or "mọi ngôn ngữ"}".')
        return 0

    # Đánh dấu nhóm chất lượng cao
    def _tier(name: str) -> str:
        n = name.lower()
        if 'chirp3-hd' in n or 'chirp-hd' in n:
            return '★★★ Chirp3-HD'
        if 'neural2' in n:
            return '★★  Neural2'
        if 'wavenet' in n:
            return '★★  Wavenet'
        if 'studio' in n:
            return '★★★ Studio'
        return '★   Standard'

    print(f'\n{len(rows)} giọng cho "{lang_prefix or "tất cả"}":\n')
    print(f'{"TÊN GIỌNG":40} {"GIỚI TÍNH":10} {"CHẤT LƯỢNG"}')
    print('-' * 75)
    for name, gender, _hz in rows:
        print(f'{name:40} {gender:10} {_tier(name)}')

    print('\nĐặt vào .env, ví dụ:')
    print(f'  GOOGLE_TTS_VOICE_NAME={rows[0][0]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
