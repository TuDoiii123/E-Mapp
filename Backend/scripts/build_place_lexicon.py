"""
Build danh mục địa danh VN cho hậu xử lý OCR (services/ocr_postcorrect.py).

Nguồn: repo madnh/hanhchinhvn (dữ liệu 3 cấp tỉnh/huyện/xã — mô hình cũ,
khớp với địa chỉ in trên giấy tờ CCCD/GPLX/kết hôn hiện hành).
Xuất: Backend/data/place_lexicon.json
  {
    "provinces": [{"code", "name"}],
    "districts": [{"code", "name", "province_code"}],
    "wards":     [{"code", "name", "district_code"}]
  }

Chạy: python scripts/build_place_lexicon.py
"""
import json
import os
import sys

import requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

RAW = 'https://raw.githubusercontent.com/madnh/hanhchinhvn/master/dist'
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'place_lexicon.json')


def fetch(name: str) -> dict:
    r = requests.get(f'{RAW}/{name}', timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    print('Tải tinh_tp / quan_huyen / xa_phuong từ madnh/hanhchinhvn ...')
    tinh = fetch('tinh_tp.json')
    huyen = fetch('quan_huyen.json')
    xa = fetch('xa_phuong.json')

    lexicon = {
        'provinces': [{'code': c, 'name': v['name']} for c, v in tinh.items()],
        'districts': [{'code': c, 'name': v['name'],
                       'province_code': v.get('parent_code', '')}
                      for c, v in huyen.items()],
        'wards':     [{'code': c, 'name': v['name'],
                       'district_code': v.get('parent_code', '')}
                      for c, v in xa.items()],
    }

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(lexicon, f, ensure_ascii=False, separators=(',', ':'))

    print(f"Đã ghi {OUT}: {len(lexicon['provinces'])} tỉnh, "
          f"{len(lexicon['districts'])} huyện, {len(lexicon['wards'])} xã")


if __name__ == '__main__':
    main()
