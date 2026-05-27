from logger import get_logger as _get_logger
_log = _get_logger("models.service_req")

"""
ServiceRequirement model — danh sách giấy tờ yêu cầu cho từng dịch vụ.
Dùng PostgreSQL với fallback về dữ liệu mặc định khi chưa có bản ghi.
"""
import uuid
from sqlalchemy import text
from models.db import db

# ── Dữ liệu mặc định theo loại thủ tục ───────────────────────────────────────
_DEFAULTS: dict[str, list[tuple]] = {
    # (doc_name, doc_description, is_required, doc_type, order_index)
    'ket_hon': [
        ('CCCD / Căn cước công dân (hai bên)', 'Bản gốc còn hiệu lực', True, 'original', 0),
        ('Giấy khai sinh', 'Bản chính hoặc bản sao có chứng thực', True, 'certified_copy', 1),
        ('Xác nhận tình trạng hôn nhân', 'Do UBND cấp xã cấp trong vòng 6 tháng', True, 'original', 2),
        ('Ảnh 4×6 cm (4 ảnh/người)', 'Ảnh chụp trong vòng 6 tháng, nền trắng', True, 'original', 3),
    ],
    'khai_sinh': [
        ('Giấy chứng sinh', 'Do cơ sở y tế cấp', True, 'original', 0),
        ('CCCD / Căn cước bố hoặc mẹ', 'Bản gốc còn hiệu lực', True, 'original', 1),
        ('Giấy đăng ký kết hôn của bố mẹ', 'Bản chính hoặc bản sao', False, 'copy', 2),
    ],
    'cccd': [
        ('CCCD cũ / Chứng minh nhân dân', 'Bản gốc hiện có', True, 'original', 0),
        ('Sổ hộ khẩu', 'Bản chính (nếu đổi theo hộ khẩu)', False, 'original', 1),
        ('Ảnh 4×6 cm (2 ảnh)', 'Ảnh chụp trong vòng 6 tháng, nền trắng', True, 'original', 2),
    ],
    'ho_khau': [
        ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 0),
        ('Hợp đồng thuê nhà / Giấy tờ nhà ở hợp lệ', 'Bản gốc hoặc bản sao công chứng', True, 'certified_copy', 1),
        ('Giấy tờ chứng minh quan hệ nhân thân', 'Nếu đăng ký theo chủ hộ', False, 'copy', 2),
        ('Đơn đăng ký thường trú (Mẫu HK01)', 'Điền đầy đủ, ký tên', True, 'original', 3),
    ],
    'dat_dai': [
        ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 0),
        ('Giấy chứng nhận QSDĐ (Sổ đỏ/Sổ hồng)', 'Bản gốc', True, 'original', 1),
        ('Hợp đồng chuyển nhượng có công chứng', 'Bản chính có chứng thực', True, 'certified_copy', 2),
        ('Biên lai nộp thuế / Giấy miễn thuế', 'Nếu có', False, 'copy', 3),
    ],
    'gplx': [
        ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 0),
        ('Giấy phép lái xe cũ', 'Bản gốc (nếu đổi)', False, 'original', 1),
        ('Giấy khám sức khoẻ', 'Cấp trong vòng 6 tháng, do cơ sở y tế cấp phép cấp', True, 'original', 2),
        ('Ảnh 3×4 cm (2 ảnh)', 'Ảnh chụp trong vòng 6 tháng, nền trắng', True, 'original', 3),
    ],
    'default': [
        ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 0),
        ('Đơn yêu cầu theo mẫu quy định', 'Điền đầy đủ thông tin và ký tên', True, 'original', 1),
        ('Giấy tờ liên quan', 'Tùy theo loại thủ tục (tham khảo cán bộ tiếp nhận)', False, 'copy', 2),
    ],
}

_KEYWORD_MAP = {
    'ket_hon':   ['kết hôn', 'ket hon', 'hon nhan', 'hôn nhân'],
    'khai_sinh': ['khai sinh', 'birth'],
    'cccd':      ['cccd', 'căn cước', 'can cuoc', 'chứng minh', 'chung minh'],
    'ho_khau':   ['hộ khẩu', 'ho khau', 'thường trú', 'thuong tru', 'cư trú'],
    'dat_dai':   ['đất đai', 'dat dai', 'quyền sử dụng', 'quyen su dung', 'sổ đỏ', 'so do'],
    'gplx':      ['giấy phép lái xe', 'gplx', 'driving', 'lái xe'],
}


def _detect_key(service_id: str) -> str:
    # Normalize slug (dang-ky-ket-hon) → space-separated (dang ky ket hon)
    # so slug-based IDs match the space-based keywords in _KEYWORD_MAP
    s = service_id.lower().replace('-', ' ').replace('_', ' ')
    for key, keywords in _KEYWORD_MAP.items():
        if any(kw in s for kw in keywords):
            return key
    return 'default'


def _rows_to_dicts(rows) -> list[dict]:
    keys = ['id', 'serviceId', 'docName', 'docDescription', 'isRequired', 'docType', 'orderIndex', 'templateFile']
    return [dict(zip(keys, r)) for r in rows]


class ServiceRequirement:
    """CRUD cho bảng service_requirements."""

    # ── Read ─────────────────────────────────────────────────────────────────

    @staticmethod
    def find_by_service_id(service_id: str) -> list[dict]:
        """
        Trả về danh sách giấy tờ yêu cầu cho service_id.
        Nếu DB chưa có → tự seed defaults rồi trả về.
        """
        try:
            sql = text('''
                SELECT id, service_id, doc_name, doc_description,
                       is_required, doc_type, order_index,
                       COALESCE(template_file, '') AS template_file
                FROM public.service_requirements
                WHERE service_id = :sid
                ORDER BY order_index
            ''')
            rows = db.session.execute(sql, {'sid': service_id}).fetchall()
            if rows:
                return _rows_to_dicts(rows)
            # Chưa có → seed và trả về
            return ServiceRequirement._seed_defaults(service_id)
        except Exception as e:
            _log.warning(f'ServiceRequirement.find_by_service_id error: {e}')
            return ServiceRequirement._make_defaults(service_id)

    # ── Write ─────────────────────────────────────────────────────────────────

    @staticmethod
    def create(data: dict) -> dict:
        req_id = data.get('id') or str(uuid.uuid4())
        sql = text('''
            INSERT INTO public.service_requirements
                (id, service_id, doc_name, doc_description, is_required, doc_type, order_index, template_file)
            VALUES (:id, :sid, :name, :desc, :req, :dtype, :order, :tmpl)
            ON CONFLICT (id) DO UPDATE SET
                doc_name        = EXCLUDED.doc_name,
                doc_description = EXCLUDED.doc_description,
                is_required     = EXCLUDED.is_required,
                doc_type        = EXCLUDED.doc_type,
                order_index     = EXCLUDED.order_index,
                template_file   = EXCLUDED.template_file
            RETURNING id, service_id, doc_name, doc_description,
                      is_required, doc_type, order_index,
                      COALESCE(template_file, '') AS template_file
        ''')
        row = db.session.execute(sql, {
            'id':    req_id,
            'sid':   data['serviceId'],
            'name':  data['docName'],
            'desc':  data.get('docDescription', ''),
            'req':   data.get('isRequired', True),
            'dtype': data.get('docType', 'original'),
            'order': data.get('orderIndex', 0),
            'tmpl':  data.get('templateFile') or None,
        }).fetchone()
        db.session.commit()
        return _rows_to_dicts([row])[0]

    @staticmethod
    def delete_by_service_id(service_id: str) -> int:
        sql = text('DELETE FROM public.service_requirements WHERE service_id = :sid')
        result = db.session.execute(sql, {'sid': service_id})
        db.session.commit()
        return result.rowcount

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _make_defaults(service_id: str) -> list[dict]:
        key = _detect_key(service_id)
        docs = _DEFAULTS.get(key, _DEFAULTS['default'])
        return [{
            'id':             f'{service_id}-req-{i}',
            'serviceId':      service_id,
            'docName':        d[0],
            'docDescription': d[1],
            'isRequired':     d[2],
            'docType':        d[3],
            'orderIndex':     d[4],
            'templateFile':   d[5] if len(d) > 5 else None,
        } for i, d in enumerate(docs)]

    @staticmethod
    def _seed_defaults(service_id: str) -> list[dict]:
        requirements = ServiceRequirement._make_defaults(service_id)
        try:
            sql = text('''
                INSERT INTO public.service_requirements
                    (id, service_id, doc_name, doc_description, is_required, doc_type, order_index, template_file)
                VALUES (:id, :sid, :name, :desc, :req, :dtype, :order, :tmpl)
                ON CONFLICT (id) DO NOTHING
            ''')
            for r in requirements:
                db.session.execute(sql, {
                    'id':    r['id'],    'sid':   r['serviceId'],
                    'name':  r['docName'], 'desc': r['docDescription'],
                    'req':   r['isRequired'], 'dtype': r['docType'],
                    'order': r['orderIndex'],
                    'tmpl':  r.get('templateFile') or None,
                })
            db.session.commit()
        except Exception as e:
            _log.warning(f'ServiceRequirement._seed_defaults error: {e}')
            db.session.rollback()
        return requirements
