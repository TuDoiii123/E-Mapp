import os
from werkzeug.security import generate_password_hash


def main(cccd='000000000000', password='admin123', email='admin@example.local', fullname='Administrator'):
    # Import FileStorage from models via relative import path at runtime
    from models.user import FileStorage

    users = FileStorage.read_json('users.json')

    # Find existing user by CCCD
    found = None
    for i, u in enumerate(users):
        if u.get('cccdNumber') == cccd:
            found = (i, u)
            break

    hashed = generate_password_hash(password, method='pbkdf2:sha256')

    if found:
        idx, user = found
        user['password'] = hashed
        user['role'] = 'admin'
        user['email'] = email
        user['fullName'] = fullname
        users[idx] = user
        FileStorage.write_json('users.json', users)
        print(f"Updated admin user {cccd} with new password.")
    else:
        # Create new admin entry
        new_user = {
            'id': str(int(__import__('time').time() * 1000)),
            'cccdNumber': cccd,
            'fullName': fullname,
            'dateOfBirth': '',
            'phone': '',
            'email': email,
            'password': hashed,
            'role': 'admin',
            'isVNeIDVerified': False,
            'vneidId': None,
            'createdAt': __import__('datetime').datetime.now().isoformat(),
            'updatedAt': __import__('datetime').datetime.now().isoformat()
        }
        users.append(new_user)
        FileStorage.write_json('users.json', users)
        print(f"Created admin user {cccd}.")


if __name__ == '__main__':
    # Allow overrides via environment variables
    cccd = os.getenv('ADMIN_CCCD', '000000000000')
    password = os.getenv('ADMIN_PASSWORD', 'admin123')
    email = os.getenv('ADMIN_EMAIL', 'admin@example.local')
    fullname = os.getenv('ADMIN_FULLNAME', 'Administrator')
    main(cccd=cccd, password=password, email=email, fullname=fullname)
