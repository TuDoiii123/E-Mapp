from ai_voice_backend.nlu import NLUEngine, Intent


def test_query_procedure_intent_preserved():
    nlu = NLUEngine()
    res = nlu._parse_gemini_response({'intent': 'QUERY_PROCEDURE', 'entities': {}})
    assert res.intent == Intent.QUERY_PROCEDURE


def test_greeting_intent_preserved():
    nlu = NLUEngine()
    res = nlu._parse_gemini_response({'intent': 'GREETING', 'entities': {}})
    assert res.intent == Intent.GREETING


def test_unknown_intent_falls_back():
    nlu = NLUEngine()
    res = nlu._parse_gemini_response({'intent': 'XYZ', 'entities': {}})
    assert res.intent == Intent.UNKNOWN
