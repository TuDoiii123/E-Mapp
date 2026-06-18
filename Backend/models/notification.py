"""
Model Notification + PushToken — lưu PostgreSQL qua db.session (raw SQL).
"""
from models.db import db
from sqlalchemy import text


def _row_to_dict(row) -> dict:
    m = row._mapping
    return {
        'id':        m['id'],
        'type':      m['type'],
        'title':     m['title'],
        'content':   m['content'] or '',
        'link':      m['link'],
        'refId':     m['ref_id'],
        'priority':  m['priority'],
        'read':      m['read_at'] is not None,
        'time':      m['created_at'].isoformat() if m['created_at'] else None,
    }


class Notification:
    @staticmethod
    def create(user_id, type, title, content='', link=None, ref_id=None, priority='low') -> dict:
        row = db.session.execute(text('''
            INSERT INTO public.notifications (user_id, type, title, content, link, ref_id, priority)
            VALUES (:uid, :type, :title, :content, :link, :ref, :prio)
            RETURNING *
        '''), {'uid': user_id, 'type': type, 'title': title, 'content': content,
               'link': link, 'ref': ref_id, 'prio': priority}).fetchone()
        db.session.commit()
        return _row_to_dict(row)

    @staticmethod
    def list_for(user_id, only_unread=False, limit=50) -> list:
        clause = 'AND read_at IS NULL' if only_unread else ''
        rows = db.session.execute(text(f'''
            SELECT * FROM public.notifications
            WHERE user_id = :uid {clause}
            ORDER BY created_at DESC LIMIT :lim
        '''), {'uid': user_id, 'lim': limit}).fetchall()
        return [_row_to_dict(r) for r in rows]

    @staticmethod
    def unread_count(user_id) -> int:
        return int(db.session.execute(text('''
            SELECT COUNT(*) FROM public.notifications WHERE user_id = :uid AND read_at IS NULL
        '''), {'uid': user_id}).scalar() or 0)

    @staticmethod
    def mark_read(notif_id, user_id) -> bool:
        res = db.session.execute(text('''
            UPDATE public.notifications SET read_at = now()
            WHERE id = :id AND user_id = :uid AND read_at IS NULL
        '''), {'id': notif_id, 'uid': user_id})
        db.session.commit()
        return res.rowcount > 0

    @staticmethod
    def mark_all_read(user_id) -> int:
        res = db.session.execute(text('''
            UPDATE public.notifications SET read_at = now()
            WHERE user_id = :uid AND read_at IS NULL
        '''), {'uid': user_id})
        db.session.commit()
        return res.rowcount


class PushToken:
    @staticmethod
    def register(user_id, token, platform='web') -> None:
        db.session.execute(text('''
            INSERT INTO public.push_tokens (token, user_id, platform)
            VALUES (:tok, :uid, :pf)
            ON CONFLICT (token) DO UPDATE SET user_id = :uid, platform = :pf
        '''), {'tok': token, 'uid': user_id, 'pf': platform})
        db.session.commit()

    @staticmethod
    def list_tokens(user_id) -> list:
        rows = db.session.execute(text('''
            SELECT token FROM public.push_tokens WHERE user_id = :uid
        '''), {'uid': user_id}).fetchall()
        return [r[0] for r in rows]

    @staticmethod
    def remove(token) -> None:
        db.session.execute(text('DELETE FROM public.push_tokens WHERE token = :tok'), {'tok': token})
        db.session.commit()
