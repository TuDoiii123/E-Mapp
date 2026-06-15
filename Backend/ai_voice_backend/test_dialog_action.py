from ai_voice_backend.dialog_action import ActionType, DialogAction


def test_action_defaults_to_empty_facts():
    a = DialogAction(ActionType.ASK_DATE)
    assert a.type == 'ASK_DATE'
    assert a.facts == {}


def test_action_carries_facts():
    a = DialogAction(ActionType.OFFER_SLOTS, {'slots': ['08:00', '09:00']})
    assert a.facts['slots'] == ['08:00', '09:00']


def test_all_action_types_are_unique_strings():
    names = [v for k, v in vars(ActionType).items() if not k.startswith('_')]
    assert len(names) == len(set(names))
    assert 'BOOKING_SUCCESS' in names
