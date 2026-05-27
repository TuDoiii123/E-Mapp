"""
link_templates.py
-----------------
Cập nhật cột template_file trong bảng service_requirements bằng cách
khớp doc_name với file template trong data/templates/.

Chạy: python scripts/link_templates.py [--dry-run]
"""
import os
import sys
import re
import argparse

# Fix Windows console encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, BASE_DIR)

# ── Mapping: (keyword_in_doc_name, template_file) ────────────────────────────
# Keyword so sánh case-insensitive, KHÔNG dấu (unicode normalize).
# Thứ tự ưu tiên: đặt rule cụ thể trước rule tổng quát.

RULES: list[tuple[list[str], str]] = [
    # === Hộ tịch / Dân sự ===
    (['khai sinh (mẫu tp', 'tờ khai đăng ký khai sinh'],
     'mau-to-khai-dang-ky-khai-sinh.doc'),

    (['khai sinh (do người yêu cầu', 'đăng ký khai sinh theo mẫu'],
     'mau-to-khai-dang-ky-khai-sinh.doc'),

    (['đăng ký kết hôn (mẫu tp', 'tờ khai đăng ký kết hôn',
      'hộ tịch điện tử tương tác đăng ký kết hôn',
      'mẫu điện tử tương tác cấp giấy xác nhận tình trạng hôn nhân'],
     'mau-to-khai-dang-ky-ket-hon.docx'),

    (['tờ khai đăng ký khai tử', 'khai tử (mẫu tp'],
     'mau-to-khai-dang-ky-khai-tu.docx'),

    (['xác nhận tình trạng hôn nhân', 'tờ khai cấp giấy xác nhận tình trạng hôn nhân'],
     'mau-to-khai-xac-nhan-tinh-trang-hon-nhan.docx'),

    # === CCCD / Cư trú ===
    (['tờ khai căn cước công dân (cc01)', 'phiếu thu nhận thông tin căn cước'],
     'mau-CC01-to-khai-CCCD.doc'),

    (['phiếu báo thay đổi hộ khẩu', 'phiếu báo thay đổi nhân khẩu',
      'tờ khai thay đổi thông tin cư trú', 'mẫu ct01', 'ct01'],
     'mau-CT01-to-khai-cu-tru.doc'),

    (['tờ khai đăng ký thường trú', 'đăng ký thường trú (mẫu hk01)', 'mẫu hk01'],
     'mau-to-khai-dang-ky-thuong-tru.docx'),

    # === Đất đai ===
    (['đơn đăng ký biến động đất đai', 'đơn đăng ký đất đai, tài sản',
      'đơn đăng ký đất đai (mẫu 09', 'mẫu 09/đk'],
     'mau-don-dang-ky-bien-dong-dat-dai.doc'),

    (['đơn đăng ký, cấp giấy chứng nhận', 'đơn đăng ký đất đai (mẫu 04a',
      'mẫu 04a/đk', 'cấp gcn quyền sử dụng đất'],
     'mau-don-cap-gcnqsdd-so-do.docx'),

    (['tờ khai lệ phí trước bạ', 'mẫu 01/lptb'],
     'mau-to-khai-le-phi-truoc-ba.docx'),

    # === Xây dựng ===
    (['đơn đề nghị cấp giấy phép xây dựng', 'đơn xin cấp phép xây dựng'],
     'mau-don-xin-cap-phep-xay-dung.docx'),

    # === Giao thông / GPLX ===
    (['đơn đề nghị cấp giấy phép lái xe', 'đơn đề nghị cấp lại/cấp đổi gplx',
      'đơn đề nghị đổi, cấp lại gplx'],
     'mau-don-de-nghi-cap-doi-gplx.docx'),

    (['giấy khám sức khỏe lái xe', 'giấy chứng nhận sức khỏe lái xe'],
     'mau-giay-kham-suc-khoe-lai-xe.doc'),

    # === Kinh doanh / Doanh nghiệp ===
    (['giấy đề nghị đăng ký hộ kinh doanh', 'đăng ký thành lập hộ kinh doanh'],
     'mau-giay-de-nghi-dang-ky-ho-kinh-doanh.docx'),

    (['giấy đề nghị đăng ký doanh nghiệp (phụ lục i-1',
      'giấy đề nghị đăng ký doanh nghiệp', 'mẫu phụ lục i-1'],
     'mau-giay-de-nghi-dang-ky-doanh-nghiep.docx'),

    # === BHXH / BHYT ===
    (['tờ khai tham gia, điều chỉnh thông tin bhxh', 'mẫu tk1-ts', 'tk1-ts'],
     'mau-to-khai-tham-gia-bhxh-bhyt.doc'),

    (['đơn đề nghị hưởng bhxh một lần', 'mẫu 14-hsb', '14-hsb'],
     'mau-don-huong-bhxh-mot-lan.docx'),

    # === Lý lịch tư pháp ===
    (['phiếu lý lịch tư pháp số 1',
      'tờ khai yêu cầu cấp phiếu lý lịch tư pháp',
      'tờ khai yêu cầu cấp phiếu lltp', 'mẫu số 03/2013/tt-btp'],
     'mau-phieu-ly-lich-tu-phap-so1.docx'),

    # === Giáo dục ===
    (['đơn miễn giảm học phí', 'miễn, giảm học phí'],
     'mau-don-mien-giam-hoc-phi.docx'),

    (['đơn đề nghị công nhận văn bằng'],
     'mau-don-de-nghi-cong-nhan-van-bang.docx'),

    # === Thuế / Hải quan ===
    (['tờ khai đăng ký thuế (mẫu 05', 'mẫu 05-đk-tct'],
     'mau-to-khai-dang-ky-thue.docx'),

    (['tờ khai thuế sử dụng đất phi nông nghiệp'],
     'mau-to-khai-thue-su-dung-dat.docx'),

    (['tờ khai thuế thu nhập cá nhân', 'khai thuế tncn'],
     'mau-to-khai-thue-thu-nhap-ca-nhan.docx'),

    # === Khác ===
    (['bản khai cá nhân (mẫu số 01', 'mẫu số 01 kèm theo quyết định số 3635'],
     'mau-ban-khai-ca-nhan.docx'),

    (['đơn xin thôi quốc tịch việt nam'],
     'mau-don-xin-thoi-quoc-tich.docx'),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize(s: str) -> str:
    """Lowercase và bỏ dấu câu không cần thiết để so sánh mềm."""
    return re.sub(r'\s+', ' ', s.lower().strip())


def match_rule(doc_name: str) -> str | None:
    """Trả về template_file nếu doc_name khớp bất kỳ rule nào."""
    dn = _normalize(doc_name)
    for keywords, tmpl_file in RULES:
        for kw in keywords:
            if _normalize(kw) in dn:
                return tmpl_file
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Link template_file vào service_requirements')
    parser.add_argument('--dry-run', action='store_true', help='Chỉ in ra không UPDATE DB')
    args = parser.parse_args()

    import logging
    logging.disable(logging.CRITICAL)
    from models.db import db
    from server import app
    from sqlalchemy import text

    templates_dir = os.path.join(BASE_DIR, 'data', 'templates')
    existing_templates = set(os.listdir(templates_dir)) if os.path.isdir(templates_dir) else set()

    with app.app_context():
        rows = db.session.execute(text(
            'SELECT id, doc_name, template_file FROM public.service_requirements ORDER BY doc_name'
        )).fetchall()

        updates: list[tuple[str, str]] = []   # (id, template_file)
        no_match: list[str] = []

        for row_id, doc_name, current_tmpl in rows:
            if current_tmpl:
                continue   # already set, skip
            matched = match_rule(doc_name)
            if matched:
                if matched not in existing_templates:
                    print(f'  [WARN] Template không tồn tại trên disk: {matched}  ← "{doc_name[:55]}"')
                updates.append((row_id, matched))
            else:
                no_match.append(doc_name)

        print(f'\nKết quả phân tích:')
        print(f'  Tổng records:         {len(rows)}')
        print(f'  Đã có template_file:  {sum(1 for _,_,t in rows if t)}')
        print(f'  Sẽ UPDATE:            {len(updates)}')
        print(f'  Không khớp rule:      {len(no_match)}')

        if no_match:
            print(f'\nDoc_names không khớp ({len(no_match)}):')
            for dn in sorted(set(no_match))[:20]:
                print(f'  ✗  {dn[:75]}')
            if len(no_match) > 20:
                print(f'  ... và {len(no_match)-20} doc_name khác')

        if updates:
            print(f'\nCác UPDATE sẽ thực hiện ({len(updates)}):')
            for rid, tmpl in updates[:15]:
                dn = next(d for i,d,_ in rows if i == rid)
                print(f'  {tmpl:50s}  ← "{dn[:45]}"')
            if len(updates) > 15:
                print(f'  ... và {len(updates)-15} record nữa')

        if args.dry_run:
            print('\n[DRY RUN] Không thực hiện UPDATE.')
            return

        if not updates:
            print('\nKhông có gì cần UPDATE.')
            return

        confirm = input(f'\nThực hiện UPDATE {len(updates)} records? [y/N] ').strip().lower()
        if confirm != 'y':
            print('Hủy.')
            return

        updated = 0
        for row_id, tmpl in updates:
            db.session.execute(
                text('UPDATE public.service_requirements SET template_file = :tmpl WHERE id = :id'),
                {'tmpl': tmpl, 'id': row_id}
            )
            updated += 1

        db.session.commit()
        print(f'\n✓ Đã UPDATE {updated} records.')

        # Verify
        result = db.session.execute(text(
            'SELECT COUNT(*) FROM public.service_requirements WHERE template_file IS NOT NULL'
        )).scalar()
        print(f'✓ Tổng records có template_file: {result}')


if __name__ == '__main__':
    main()
