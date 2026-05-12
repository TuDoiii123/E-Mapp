"""
VNeID verification service.

TODO: Thay thế bằng VNeID API thật khi có credentials:
  - Endpoint: https://dichvucong.gov.vn/api/vneid/verify
  - Docs: https://dichvucong.gov.vn/developer

Hiện tại: mock cho phép demo/dev.
"""
import os
from datetime import datetime


def verify_vneid(cccd_number: str) -> dict | None:
    """Xác thực CCCD qua VNeID. Mock trả về thông tin demo."""
    if not cccd_number or len(str(cccd_number)) != 12 or not str(cccd_number).isdigit():
        return None
    return {
        'id':           f'vneid_{cccd_number}',
        'cccdNumber':   cccd_number,
        'verified':     True,
        'verifiedAt':   datetime.utcnow().isoformat() + 'Z',
        'fullName':     'Nguyễn Văn A',
        'dateOfBirth':  '1990-01-01',
        'address':      'Thanh Hóa, Việt Nam',
    }


def get_vneid_user_info(vneid_id: str) -> dict | None:
    if not vneid_id:
        return None
    return {
        'id':                vneid_id,
        'verified':          True,
        'verificationLevel': 'level2',
        'verifiedAt':        datetime.utcnow().isoformat() + 'Z',
    }


def is_vneid_available() -> bool:
    return True


# Backward-compat aliases (tên cũ camelCase)
verifyVNeID       = verify_vneid
getVNeIDUserInfo  = get_vneid_user_info
isVNeIDAvailable  = is_vneid_available
