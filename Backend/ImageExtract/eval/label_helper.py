"""
Hỗ trợ gán nhãn ảnh thật / ảnh specimen: chạy Gemini 1 lần trên ảnh chưa có
nhãn, ghi kết quả thành NHÁP nhãn để sửa tay — đỡ phải gõ JSON từ đầu.

⚠ Nhãn nháp là dự đoán của model, PHẢI kiểm tra và sửa tay trước khi dùng
làm ground truth (nếu không thì đang lấy model chấm chính nó).

Usage:
    python label_helper.py anh_cccd.jpg --doc-type cccd
    python label_helper.py mau_don.png --doc-type form
Ảnh sẽ được copy vào dataset/images/, nhãn nháp ghi vào dataset/labels/.
"""
import argparse
import json
import os
import shutil
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')  # console Windows mặc định cp1252

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(HERE, '..', '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

DATASET_DIR = os.path.join(HERE, 'dataset')

from scoring import DOC_KEYS  # noqa: E402 — khóa schema chuẩn theo prompt


def main():
    ap = argparse.ArgumentParser(description='Sinh nhãn nháp cho ảnh thật')
    ap.add_argument('image', help='đường dẫn ảnh cần gán nhãn')
    ap.add_argument('--doc-type', required=True,
                    choices=['cccd', 'gplx', 'marriage', 'form'])
    ap.add_argument('--variant', default='clean',
                    choices=['clean', 'blur', 'tilt', 'dark'])
    args = ap.parse_args()

    if not os.path.exists(args.image):
        sys.exit(f'Không thấy ảnh: {args.image}')

    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BACKEND_DIR, '.env'))
    except ImportError:
        pass

    from services.image_extractor import extract_document, extract_form_template

    print(f'Gọi Gemini cho {args.image} ...')
    if args.doc_type == 'form':
        data = extract_form_template(args.image)
        expected = {
            'formName': data.get('formName'),
            'formCode': data.get('formCode'),
            'fields': [f.get('label') or f.get('fieldName')
                       for f in (data.get('fields') or []) if isinstance(f, dict)],
        }
    else:
        data = extract_document(args.image)
        expected = {k: data.get(k) for k in DOC_KEYS[args.doc_type]}

    # Copy ảnh vào dataset, đặt tên real_*
    images_dir = os.path.join(DATASET_DIR, 'images')
    labels_dir = os.path.join(DATASET_DIR, 'labels')
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    base = os.path.basename(args.image)
    stem = f"{args.doc_type}_real_{os.path.splitext(base)[0]}_{args.variant}"
    ext = os.path.splitext(base)[1].lower()
    shutil.copy2(args.image, os.path.join(images_dir, stem + ext))

    label = {
        'image': stem + ext,
        'docType': args.doc_type,
        'variant': args.variant,
        'source': 'real_draft',   # đổi thành 'real' sau khi đã kiểm tra tay
        'expected': expected,
    }
    label_path = os.path.join(labels_dir, stem + '.json')
    with open(label_path, 'w', encoding='utf-8') as f:
        json.dump(label, f, ensure_ascii=False, indent=2)

    print(f'Đã ghi nhãn NHÁP: {label_path}')
    print('⚠ Mở file, kiểm tra & sửa từng trường, rồi đổi "source" thành "real".')


if __name__ == '__main__':
    main()
