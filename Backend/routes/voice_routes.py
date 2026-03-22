"""
Voice routes: STT, TTS, dialog flow, auto-create appointment.
Dialog state is persisted to data/dialog_store.json so it survives restarts.
"""
import base64
import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Blueprint, Response, jsonify, make_response, request

from services.appointments import create_appointment, suggest_slots

voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')

# ── Gemini (lazy init) ─────────────────────────────────────────────────────────
_gemini_model = None


def _get_gemini():
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model
    api_key = os.getenv('GEMINI_API_KEY')
    model_name = os.getenv('GEMINI_MODEL_NAME', 'models/gemini-2.5-flash-lite')
    if not api_key:
        return None
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel(model_name)
    except Exception as exc:
        print('[Gemini][voice] Init failed:', exc)
    return _gemini_model


# ── Google Cloud TTS/STT (lazy) ────────────────────────────────────────────────
def _get_speech_client():
    try:
        from google.cloud import speech as g_speech  # type: ignore
        return g_speech.SpeechClient()
    except Exception:
        return None


def _get_tts_client():
    try:
        from google.cloud import texttospeech as g_tts  # type: ignore
        return g_tts.TextToSpeechClient()
    except Exception:
        return None


def _tts_mp3_base64(text: str) -> Optional[str]:
    try:
        from google.cloud import texttospeech as g_tts  # type: ignore
    except Exception:
        return None
    client = _get_tts_client()
    if client is None:
        return None
    try:
        voice_name = os.getenv('GOOGLE_TTS_VOICE_NAME')
        speaking_rate = float(os.getenv('GOOGLE_TTS_SPEAKING_RATE', '1.0'))
        pitch = float(os.getenv('GOOGLE_TTS_PITCH', '0.0'))
        voice_params: Dict[str, Any] = {'language_code': 'vi-VN', 'ssml_gender': g_tts.SsmlVoiceGender.NEUTRAL}
        if voice_name:
            voice_params = {'name': voice_name}
        res = client.synthesize_speech(
            input=g_tts.SynthesisInput(text=text),
            voice=g_tts.VoiceSelectionParams(**voice_params),
            audio_config=g_tts.AudioConfig(
                audio_encoding=g_tts.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
            ),
        )
        return base64.b64encode(res.audio_content).decode('ascii')
    except Exception:
        return None


def _call_gemini_json(prompt: str, tag: str = 'GENERIC') -> Dict[str, Any]:
    model = _get_gemini()
    if model is None:
        return {}
    try:
        resp = model.generate_content(prompt)
        raw = (getattr(resp, 'text', None) or '').strip()
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return {}
        return json.loads(m.group(0))
    except Exception as e:
        print(f'[Gemini:{tag}] Error:', repr(e))
        return {}


# ── Dialog state persistence ───────────────────────────────────────────────────
_DIALOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'dialog_store.json')
_AUTO_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'auto_state_store.json')


def _load_store(path: str) -> Dict[str, Any]:
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_store(path: str, data: Dict[str, Any]) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── Dialog step constants ──────────────────────────────────────────────────────
class _Step:
    ASK_INTENT = 'ASK_INTENT'
    ASK_LOCATION = 'ASK_LOCATION'
    ASK_DATE = 'ASK_DATE'
    SUGGEST_SLOT = 'SUGGEST_SLOT'
    CONFIRM = 'CONFIRM'
    DONE = 'DONE'


# ── Parsing helpers ────────────────────────────────────────────────────────────
def _parse_date_vi(text_in: str) -> Optional[str]:
    m = re.search(r'(20\d{2})-(\d{1,2})-(\d{1,2})', text_in)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f'{y:04d}-{mo:02d}-{d:02d}'
    m = re.search(r'(\d{1,2})/(\d{1,2})/(20\d{2})', text_in)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f'{y:04d}-{mo:02d}-{d:02d}'
    return None


def _extract_time(text_in: str, allowed: Optional[List[str]] = None) -> Optional[str]:
    m = re.search(r'\b(\d{1,2})(?:[:hH ](\d{2}))\b', text_in)
    if m:
        cand = f'{int(m.group(1)):02d}:{int(m.group(2)):02d}:00'
        if not allowed or cand in allowed:
            return cand
    m = re.search(r'\b(\d{1,2})\s*(?:giờ|h)\b', text_in)
    if m:
        cand = f'{int(m.group(1)):02d}:00:00'
        if not allowed or cand in allowed:
            return cand
    return None


def _svc_code(text: str) -> str:
    t = text.lower()
    if 'căn cước' in t or 'cccd' in t:
        return 'CCCD'
    if 'khai sinh' in t:
        return 'KHAISINH'
    if 'hộ chiếu' in t or 'passport' in t:
        return 'PASSPORT'
    return 'SERVICE_CODE'


def _agency_id(location: str) -> str:
    loc = (location or '').lower()
    return 'ubnd-001' if ('ubnd' in loc or 'ủy ban' in loc) else 'agency-001'


def _success_msg(date_iso: str, hhmm: str, location_display: str, service_display: str,
                 info: str, queue: int, appt_id: str) -> str:
    return (
        'Đặt lịch thành công, thông tin chi tiết đặt lịch:\n'
        f'Thời gian: {date_iso} {hhmm}\n'
        f'Địa điểm: {location_display}\n'
        f'Dịch vụ: {service_display}\n'
        f'Mục đích: {info}\n'
        f'Mã số: {queue}\n'
        f'Mã ID: {appt_id}'
    )


# ── STT ────────────────────────────────────────────────────────────────────────
@voice_bp.route('/stt', methods=['POST'])
def api_voice_stt():
    if request.content_type and 'multipart/form-data' in request.content_type.lower():
        file = request.files.get('file')
    else:
        file = None
    if file is None:
        return jsonify({'status': 'error', 'message': 'Thiếu file audio trong form-data (field "file")'}), 200
    client = _get_speech_client()
    if client is None:
        if os.getenv('VOICE_STT_DEV_MOCK', '1') == '1':
            debug_text = request.headers.get('X-Debug-Transcription') or 'đặt lịch căn cước ngày mai 09:00'
            return jsonify({'status': 'success', 'text': debug_text}), 200
        return jsonify({'status': 'error', 'message': 'Google Speech chưa được cấu hình'}), 200
    try:
        from google.cloud import speech as g_speech  # type: ignore
        audio_bytes = file.read()
        audio = g_speech.RecognitionAudio(content=audio_bytes)
        config = g_speech.RecognitionConfig(
            encoding=g_speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            language_code='vi-VN',
            enable_automatic_punctuation=True,
        )
        res = client.recognize(config=config, audio=audio)
        if not res.results:
            return jsonify({'status': 'error', 'message': 'Không nghe thấy gì trong audio.'}), 200
        text_out = ' '.join([r.alternatives[0].transcript for r in res.results]).strip()
        return jsonify({'status': 'success', 'text': text_out}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 200


# ── TTS ────────────────────────────────────────────────────────────────────────
@voice_bp.route('/tts', methods=['POST'])
def api_voice_tts():
    payload = request.get_json(silent=True) or {}
    text = (payload.get('text') or '').strip()
    if not text:
        return jsonify({'status': 'error', 'message': 'Thiếu text cho TTS'}), 400
    client = _get_tts_client()
    if client is None:
        return jsonify({'status': 'error', 'message': 'Google TTS chưa được cấu hình'}), 500
    try:
        from google.cloud import texttospeech as g_tts  # type: ignore
        res = client.synthesize_speech(
            input=g_tts.SynthesisInput(text=text),
            voice=g_tts.VoiceSelectionParams(language_code='vi-VN', ssml_gender=g_tts.SsmlVoiceGender.NEUTRAL),
            audio_config=g_tts.AudioConfig(audio_encoding=g_tts.AudioEncoding.MP3),
        )
        return Response(res.audio_content, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@voice_bp.route('/voices', methods=['GET'])
def api_voice_list_voices():
    client = _get_tts_client()
    if client is None:
        return jsonify({'success': False, 'message': 'Google TTS chưa được cấu hình'}), 500
    try:
        from google.cloud import texttospeech as g_tts  # type: ignore
        lang = request.args.get('lang') or None
        resp = client.list_voices()
        voices = []
        for v in resp.voices:
            langs = list(v.language_codes)
            if lang and lang not in langs:
                continue
            voices.append({
                'name': v.name,
                'languageCodes': langs,
                'ssmlGender': g_tts.SsmlVoiceGender(v.ssml_gender).name if hasattr(v, 'ssml_gender') else None,
                'naturalSampleRateHertz': getattr(v, 'natural_sample_rate_hertz', None),
            })
        return jsonify({'success': True, 'data': {'voices': voices}})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Auto-create (one-shot NLP → appointment) ───────────────────────────────────
@voice_bp.route('/appointments/auto-create', methods=['POST'])
def api_voice_auto_create():
    payload = request.get_json(silent=True) or {}
    user_text = (payload.get('text') or '').strip()
    phone = (payload.get('phone') or '').strip() or None
    session_id = (payload.get('session_id') or payload.get('sessionId') or 'default').strip() or 'default'
    speak = bool(payload.get('speak') or os.getenv('VOICE_DIALOG_TTS', '1') == '1')
    if not user_text:
        return jsonify({'status': 'error', 'message': 'Thiếu text.'}), 400

    auto_store = _load_store(_AUTO_FILE)
    agg = auto_store.get(session_id) or {
        'service_type': None, 'location': None,
        'appointment_date': None, 'appointment_time': None,
    }

    model = _get_gemini()
    if model is not None:
        prompt = (
            'Bạn là trợ lý hành chính công Việt Nam.\n'
            'Nhiệm vụ: Đọc câu tiếng Việt và trích xuất thông tin đặt lịch hẹn thủ tục hành chính.\n'
            'Chỉ trả lời đúng JSON hợp lệ, không giải thích thêm.\n'
            'Trường cần trích xuất: service_type, location, appointment_date (YYYY-MM-DD), appointment_time (HH:MM:SS), phone, citizen_name, note.\n\n'
            f'Câu người dùng:\n"{user_text}".'
        )
        data = _call_gemini_json(prompt, 'AUTO_CREATE')
    else:
        data = {}

    service_type = data.get('service_type') or agg.get('service_type')
    location = data.get('location') or agg.get('location')
    date_iso = data.get('appointment_date') or agg.get('appointment_date') or _parse_date_vi(user_text)
    appt_time = data.get('appointment_time') or agg.get('appointment_time') or _extract_time(user_text)

    missing = [k for k, v in [
        ('service_type', service_type), ('location', location),
        ('appointment_date', date_iso), ('appointment_time', appt_time),
    ] if not v]

    # Persist partial state
    agg.update({'service_type': service_type, 'location': location,
                'appointment_date': date_iso, 'appointment_time': appt_time})
    auto_store[session_id] = agg
    _save_store(_AUTO_FILE, auto_store)

    if missing:
        prompts_map = {
            'service_type': 'Bạn muốn làm thủ tục gì? Ví dụ: làm căn cước công dân.',
            'location': 'Bạn muốn làm ở đâu? Bạn có thể nói tên quận/huyện hoặc cơ quan.',
            'appointment_date': 'Bạn có thể cung cấp ngày (YYYY-MM-DD hoặc DD/MM/YYYY) để mình gợi ý khung giờ trống?',
            'appointment_time': 'Bạn thích khung giờ nào? Ví dụ: 09:00 hoặc 14:00.',
        }
        first = missing[0]
        extra: Dict[str, Any] = {}
        if first == 'appointment_time' and location and date_iso:
            try:
                extra['suggestedSlots'] = suggest_slots(date_iso, _agency_id(location))
            except Exception:
                pass
        return jsonify({'status': 'continue', 'message': prompts_map.get(first, 'Bạn có thể cung cấp thêm thông tin?'),
                        'next': first, 'state': agg, **extra}), 200

    try:
        dt_obj = datetime.strptime(date_iso, '%Y-%m-%d')  # noqa: F841
        t_obj = datetime.strptime(appt_time, '%H:%M:%S')
        hhmm = t_obj.strftime('%H:%M')
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Định dạng ngày/giờ không hợp lệ: {e}'}), 200

    svc = _svc_code(service_type or '')
    aid = _agency_id(location or '')
    ok, appt, err = create_appointment({
        'agencyId': aid,
        'serviceCode': svc,
        'date': date_iso,
        'time': hhmm,
        'phone': phone or data.get('phone'),
        'fullName': data.get('citizen_name') or 'Người dân',
        'info': data.get('note') or 'Đặt lịch qua voice',
    })
    if not ok:
        return jsonify({'status': 'error', 'message': err or 'Không tạo được lịch'}), 200

    # Clear session state after success
    auto_store.pop(session_id, None)
    _save_store(_AUTO_FILE, auto_store)

    loc_display = location or ('UBND Quận' if aid == 'ubnd-001' else 'Cơ quan hành chính')
    svc_display = service_type or {'CCCD': 'Làm CCCD', 'KHAISINH': 'Đăng ký khai sinh',
                                    'PASSPORT': 'Làm hộ chiếu'}.get(svc, 'Dịch vụ hành chính')
    msg = _success_msg(date_iso, hhmm, loc_display, svc_display,
                       appt.get('info') or 'Đặt lịch qua voice',
                       appt.get('queueNumber', 1), appt.get('id', ''))
    resp_payload: Dict[str, Any] = {'status': 'success', 'message': msg, 'missing': None, 'appointment': appt}
    if speak:
        audio_b64 = _tts_mp3_base64(msg)
        if audio_b64:
            resp_payload['audio'] = {'mimeType': 'audio/mpeg', 'base64': audio_b64}
    return jsonify(resp_payload)


# ── Dialog flow ────────────────────────────────────────────────────────────────
def _dialog_suggest_slots(state: Dict[str, Any]) -> tuple:
    loc = state.get('location')
    date_iso = state.get('appointment_date')
    if not loc or not date_iso:
        state['step'] = _Step.ASK_DATE
        return ('Để gợi ý giờ trống, mình cần biết rõ ngày và địa điểm nhé.', state)
    aid = _agency_id(loc)
    available = suggest_slots(date_iso, aid)
    if not available:
        state['step'] = _Step.ASK_DATE
        return (f'Ngày {date_iso} tại {loc} sẽ khá đông. Vui lòng cung cấp ngày khác để em gợi ý khung giờ trống nhé.', state)
    state['suggested_slots'] = available
    state['step'] = _Step.CONFIRM
    times_text = ', '.join(s[:5] for s in available)
    return (f'Ngày {date_iso} tại {loc} còn trống các khung giờ: {times_text}. Anh/chị muốn chọn giờ nào ạ?', state)


@voice_bp.route('/dialog', methods=['POST'])
def api_voice_dialog():
    payload = request.get_json(silent=True) or {}
    session_id = (payload.get('session_id') or payload.get('sessionId') or 'default').strip() or 'default'
    user_text = (payload.get('text') or '').strip()
    phone = (payload.get('phone') or '').strip() or None
    speak = bool(payload.get('speak') or os.getenv('VOICE_DIALOG_TTS', '0') == '1')

    dialog_store = _load_store(_DIALOG_FILE)

    def _reply(reply_text: str, step: str, done: bool, state_obj: Any, extra: Optional[Dict] = None):
        resp: Dict[str, Any] = {'reply': reply_text, 'step': step, 'done': done, 'state': state_obj}
        if speak and reply_text:
            audio_b64 = _tts_mp3_base64(reply_text)
            if audio_b64:
                resp['audio'] = {'mimeType': 'audio/mpeg', 'base64': audio_b64}
        if extra:
            resp.update(extra)
        return jsonify(resp)

    if not user_text:
        return _reply('Mình chưa nghe rõ, anh/chị có thể nói lại giúp em được không?', _Step.ASK_INTENT, False, None)

    state = dialog_store.get(session_id)
    if state is None:
        state = {
            'step': _Step.ASK_INTENT,
            'citizen_name': None, 'phone': phone,
            'service_type': None, 'location': None,
            'appointment_date': None, 'appointment_time': None,
            'note': None, 'suggested_slots': None,
        }
        dialog_store[session_id] = state

    # DONE — allow restart
    if state.get('step') == _Step.DONE:
        if re.search(r'(đặt lịch|thủ tục|căn cước|cccd|hồ sơ|khai sinh)', user_text, re.IGNORECASE):
            state.update({'step': _Step.ASK_INTENT, 'service_type': None, 'location': None,
                          'appointment_date': None, 'appointment_time': None,
                          'note': None, 'suggested_slots': None})
        else:
            _save_store(_DIALOG_FILE, dialog_store)
            return _reply('Lịch hẹn trước đó đã được đặt xong. Nếu muốn đặt lịch mới, hãy nói thủ tục bạn cần.',
                          state['step'], True, state)

    # ASK_INTENT
    if state.get('step') == _Step.ASK_INTENT:
        service_type = None
        model = _get_gemini()
        if model is not None:
            data = _call_gemini_json(
                f'Hãy trích service_type từ: \n\n"""{user_text}""". Trả JSON {{"service_type": string hoặc null}}.', 'ASK_INTENT')
            service_type = data.get('service_type') if isinstance(data, dict) else None
        if not service_type:
            if re.search(r'căn cước|cccd', user_text, re.I):
                service_type = 'Làm căn cước công dân'
            elif re.search(r'khai sinh', user_text, re.I):
                service_type = 'Đăng ký khai sinh'
        if not service_type:
            _save_store(_DIALOG_FILE, dialog_store)
            return _reply('Bạn muốn làm thủ tục gì? Ví dụ: "Tôi muốn đặt lịch làm thủ tục CCCD".', _Step.ASK_INTENT, False, state)
        state['service_type'] = service_type
        state['step'] = _Step.ASK_LOCATION
        _save_store(_DIALOG_FILE, dialog_store)
        return _reply(f'Bạn muốn {service_type.lower()} ở đâu? Ví dụ: UBND quận Hoàn Kiếm.', state['step'], False, state)

    # ASK_LOCATION
    if state.get('step') == _Step.ASK_LOCATION:
        location = None
        model = _get_gemini()
        if model is not None:
            data = _call_gemini_json(
                f'Trích location từ: \n\n"""{user_text}""". Trả JSON {{"location": string hoặc null}}.', 'ASK_LOCATION')
            location = data.get('location') if isinstance(data, dict) else None
        if not location:
            m = re.search(r'(ubnd[^,.]*|ủy ban[^,.]*)', user_text, re.I)
            if m:
                location = m.group(1)
        if not location:
            _save_store(_DIALOG_FILE, dialog_store)
            return _reply('Bạn muốn làm ở đâu? Bạn có thể nói tên quận/huyện hoặc cơ quan.', _Step.ASK_LOCATION, False, state)
        try:
            from services.distance import suggest_nearest_office  # type: ignore
            nearest = suggest_nearest_office(user_text)
        except Exception:
            nearest = None
        state['location'] = nearest or location
        state['step'] = _Step.ASK_DATE
        _save_store(_DIALOG_FILE, dialog_store)
        return _reply(
            f'Địa chỉ bạn muốn tới là {state["location"]}, bạn có thể cung cấp ngày để tôi lựa chọn khung giờ phù hợp nhất.',
            state['step'], False, state)

    # ASK_DATE
    if state.get('step') == _Step.ASK_DATE:
        appt_date = None
        model = _get_gemini()
        if model is not None:
            data = _call_gemini_json(
                f'Trích appointment_date (YYYY-MM-DD) từ: \n\n"""{user_text}""". Trả JSON {{"appointment_date": string hoặc null}}.', 'ASK_DATE')
            appt_date = data.get('appointment_date') if isinstance(data, dict) else None
        if not appt_date:
            appt_date = _parse_date_vi(user_text)
        if not appt_date:
            _save_store(_DIALOG_FILE, dialog_store)
            return _reply('Anh/chị vui lòng cho biết ngày cụ thể nhé.', _Step.ASK_DATE, False, state)
        state['appointment_date'] = appt_date
        reply, new_state = _dialog_suggest_slots(state)
        dialog_store[session_id] = new_state
        _save_store(_DIALOG_FILE, dialog_store)
        return _reply(reply, new_state['step'], False, new_state)

    # SUGGEST_SLOT
    if state.get('step') == _Step.SUGGEST_SLOT:
        reply, new_state = _dialog_suggest_slots(state)
        dialog_store[session_id] = new_state
        _save_store(_DIALOG_FILE, dialog_store)
        return _reply(reply, new_state['step'], False, new_state)

    # CONFIRM
    if state.get('step') == _Step.CONFIRM:
        slots = state.get('suggested_slots') or []
        if not slots:
            reply, new_state = _dialog_suggest_slots(state)
            dialog_store[session_id] = new_state
            _save_store(_DIALOG_FILE, dialog_store)
            return _reply(reply, new_state['step'], False, new_state)

        appt_time = None
        model = _get_gemini()
        if model is not None:
            data = _call_gemini_json(
                f'Các khung giờ gợi ý: {slots}. Từ câu sau, trích appointment_time (HH:MM:SS) nếu phù hợp. Câu: "{user_text}". Trả JSON {{"appointment_time": string hoặc null}}.', 'CONFIRM_SLOT')
            appt_time = data.get('appointment_time') if isinstance(data, dict) else None
            if appt_time and len(appt_time) == 5:
                for s in slots:
                    if s.startswith(appt_time):
                        appt_time = s
                        break
        if not appt_time:
            m = re.search(r'\b(\d{1,2}):(\d{2})\b', user_text)
            if m:
                cand = f'{int(m.group(1)):02d}:{m.group(2)}:00'
                if cand in slots:
                    appt_time = cand
        if not appt_time or appt_time not in slots:
            _save_store(_DIALOG_FILE, dialog_store)
            return _reply('Anh/chị vui lòng chọn một trong các khung giờ em vừa gợi ý nhé.', _Step.CONFIRM, False, state)

        state['appointment_time'] = appt_time
        date_iso = state.get('appointment_date')
        hhmm = appt_time[:5]
        svc = _svc_code(state.get('service_type') or '')
        loc = state.get('location') or ''
        aid = _agency_id(loc)
        ok, appt, err = create_appointment({
            'agencyId': aid,
            'serviceCode': svc,
            'date': date_iso,
            'time': hhmm,
            'phone': state.get('phone'),
            'fullName': state.get('citizen_name') or 'Người dân',
            'info': 'Đặt lịch qua voicebot',
        })
        if not ok:
            _save_store(_DIALOG_FILE, dialog_store)
            return _reply(err or 'Không tạo được lịch', _Step.CONFIRM, False, state)

        state['step'] = _Step.DONE
        dialog_store[session_id] = state
        _save_store(_DIALOG_FILE, dialog_store)

        d_str = datetime.strptime(date_iso, '%Y-%m-%d').strftime('%d/%m/%Y') if date_iso else ''
        svc_display = state.get('service_type') or {'CCCD': 'Làm CCCD', 'KHAISINH': 'Đăng ký khai sinh',
                                                     'PASSPORT': 'Làm hộ chiếu'}.get(svc, 'Dịch vụ hành chính')
        loc_display = loc or ('UBND Quận' if aid == 'ubnd-001' else 'Cơ quan hành chính')
        msg = _success_msg(d_str, hhmm, loc_display, svc_display,
                           appt.get('info') or 'Đặt lịch qua voicebot',
                           appt.get('queueNumber', 1), appt.get('id', ''))
        return _reply(msg, state['step'], True, state, {'appointment': appt})

    _save_store(_DIALOG_FILE, dialog_store)
    return _reply('Mình đang gặp lỗi kỹ thuật, anh/chị thử nói lại giúp em được không?',
                  state.get('step') or _Step.ASK_INTENT, False, state)
