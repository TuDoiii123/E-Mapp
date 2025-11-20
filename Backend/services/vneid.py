import asyncio
from datetime import datetime


async def verify_vneid(cccd_number: str):
    """Mock VNeID verification for demo purposes."""
    # Simulate network delay
    await asyncio.sleep(0.25)

    if not cccd_number or len(str(cccd_number)) != 12 or not str(cccd_number).isdigit():
        return None

    return {
        'id': f'vneid_{cccd_number}',
        'cccdNumber': cccd_number,
        'verified': True,
        'verifiedAt': datetime.utcnow().isoformat() + 'Z',
        'fullName': None,
        'dateOfBirth': None,
        'address': None
    }


async def get_vneid_user_info(vneid_id: str):
    await asyncio.sleep(0.15)
    if not vneid_id:
        return None
    return {
        'id': vneid_id,
        'verified': True,
        'verificationLevel': 'level2',
        'verifiedAt': datetime.utcnow().isoformat() + 'Z'
    }


async def is_vneid_available():
    return True


# Synchronous wrappers for earlier code that expects sync functions
def verifyVNeID(cccd_number: str):
    import asyncio
    return asyncio.get_event_loop().run_until_complete(verify_vneid(cccd_number))


def getVNeIDUserInfo(vneid_id: str):
    import asyncio
    return asyncio.get_event_loop().run_until_complete(get_vneid_user_info(vneid_id))


def isVNeIDAvailable():
    return True
