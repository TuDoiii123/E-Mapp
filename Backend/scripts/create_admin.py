import os
from models.user import User


def main():
    # Read admin details from environment or use safe defaults for local dev
    admin_cccd = os.getenv('ADMIN_CCCD', '000000000000')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.local')
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin@123!')
    admin_fullname = os.getenv('ADMIN_FULLNAME', 'Administrator')

    # Check existing by email or cccd
    existing_by_email = User.find_by_email(admin_email)
    existing_by_cccd = User.find_by_cccd(admin_cccd)

    if existing_by_email or existing_by_cccd:
        print('Admin user already exists:')
        if existing_by_email:
            print(' - Found by email:', admin_email)
        if existing_by_cccd:
            print(' - Found by CCCD:', admin_cccd)
        return

    user_payload = {
        'cccdNumber': admin_cccd,
        'fullName': admin_fullname,
        'dateOfBirth': '',
        'phone': '',
        'email': admin_email,
        'password': admin_password,
        'role': 'admin'
    }

    try:
        created = User.create(user_payload)
        print('Admin user created successfully:')
        print(' - id:', created.get('id'))
        print(' - email:', created.get('email'))
        print(' - cccd:', created.get('cccdNumber'))
        print('IMPORTANT: Change the password and JWT_SECRET for production.')
    except Exception as e:
        print('Failed to create admin user:', e)


if __name__ == '__main__':
    main()
