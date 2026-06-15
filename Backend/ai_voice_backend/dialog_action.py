"""
DialogAction — "ý định giao tiếp" có cấu trúc do FSM xuất ra.

Tách "sự thật" (loại action + facts) khỏi "câu chữ" (do ResponseGenerator sinh).
Đặt ở module riêng để dialog_manager và response_generator cùng import mà không vòng.
"""
from dataclasses import dataclass, field
from typing import Any, Dict


class ActionType:
    GREET            = 'GREET'
    ASK_INTENT       = 'ASK_INTENT'
    ASK_LOCATION     = 'ASK_LOCATION'
    ASK_DATE         = 'ASK_DATE'
    OFFER_SLOTS      = 'OFFER_SLOTS'
    NO_SLOTS         = 'NO_SLOTS'
    ASK_TIME_AGAIN   = 'ASK_TIME_AGAIN'
    CONFIRM_DETAILS  = 'CONFIRM_DETAILS'
    SLOT_TAKEN       = 'SLOT_TAKEN'
    BOOKING_SUCCESS  = 'BOOKING_SUCCESS'
    BOOKING_ERROR    = 'BOOKING_ERROR'
    ANSWER_PROCEDURE = 'ANSWER_PROCEDURE'
    SMALL_TALK       = 'SMALL_TALK'
    CANCELLED        = 'CANCELLED'
    ALREADY_DONE     = 'ALREADY_DONE'


@dataclass
class DialogAction:
    type:  str
    facts: Dict[str, Any] = field(default_factory=dict)
