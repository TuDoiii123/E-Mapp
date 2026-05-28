"""
fill_procedures_steps.py  v2
Dien steps + conditions cho cac thu tuc slug-ID con thieu.
Noi dung duoc chuan hoa tu du lieu DVC (chitiet_dvc_tructuyen / chitiet_thutuc)
ket hop viet tay cho cac thu tuc khong co trong DB.
Khong xoa du lieu da co (WHERE steps IS NULL OR steps = '').
"""
import sys
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

DATA = {
    # ── Civil ─────────────────────────────────────────────────────────────
    'dang-ky-ket-hon': {
        'steps': (
            "Buoc 1: Hai ben nam nu chuan bi ho so gom To khai dang ky ket hon (Mau HTT-2014-01.1), "
            "CCCD / Can cuoc cong dan cua ca hai ben con hieu luc, Xac nhan tinh trang hon nhan do UBND "
            "cap xa cap trong vong 6 thang.\n"
            "Buoc 2: Nop ho so truc tiep tai Bo phan mot cua UBND cap xa co tham quyen hoac nop truc "
            "tuyen qua Cong DVC quoc gia / tinh Thanh Hoa.\n"
            "Buoc 3: Can bo tu phap kiem tra tinh hop le cua ho so; yeu cau bo sung neu thieu. Thoi han "
            "giai quyet: trong ngay lam viec (nuoc ngoai 5 ngay lam viec).\n"
            "Buoc 4: Can bo tu phap to chuc le dang ky ket hon, yeu cau hai ben xac nhan vao So dang ky "
            "ket hon; cap Giay chung nhan dang ky ket hon cho moi ben 01 ban."
        ),
        'conditions': (
            "Nam tu du 20 tuoi tro len, nu tu du 18 tuoi tro len.\n"
            "Viec ket hon do nam va nu tu nguyen quyet dinh, khong bi ep buoc hoac lua doi.\n"
            "Cac ben khong bi mat nang luc hanh vi dan su.\n"
            "Hai ben khong thuoc truong hop cam ket hon theo Luat Hon nhan va Gia dinh 2014."
        ),
    },
    'dang-ky-khai-sinh': {
        'steps': (
            "Buoc 1: Cha hoac me (hoac nguoi co trach nhiem) chuan bi ho so gom Giay chung sinh do co "
            "so y te cap, CCCD cua cha/me, Giay dang ky ket hon cua cha me (neu co).\n"
            "Buoc 2: Nop ho so tai Bo phan mot cua UBND cap xa noi cu tru cua me (hoac cha neu me khong "
            "co noi cu tru o Viet Nam), hoac nop truc tuyen qua Cong DVC.\n"
            "Buoc 3: Can bo tu phap kiem tra ho so; neu hop le ghi vao So dang ky khai sinh. Thoi han "
            "giai quyet: trong ngay lam viec hoac cham nhat ngay lam viec tiep theo.\n"
            "Buoc 4: Nguoi yeu cau nhan Trich luc khai sinh (01 ban chich thuc) tai bo phan mot cua."
        ),
        'conditions': (
            "Dang ky khai sinh thuc hien trong vong 60 ngay ke tu ngay sinh.\n"
            "Tre sinh song trong thoi gian du 24 gio moi lam the tuc dang ky.\n"
            "Truong hop dang ky qua han can giai trinh ly do va co xac nhan cua UBND."
        ),
    },
    'dang-ky-khai-tu': {
        'steps': (
            "Buoc 1: Than nhan hoac nguoi co trach nhiem chuan bi ho so gom To khai dang ky khai tu "
            "(Mau HTT-2014-03.2), Giay bao tu / bien ban xac nhan chet do co quan y te / cong an cap.\n"
            "Buoc 2: Nop ho so tai Bo phan mot cua UBND cap xa noi cu tru cuoi cung cua nguoi qua doi "
            "hoac noi nguoi do chet; hoac nop truc tuyen qua Cong DVC.\n"
            "Buoc 3: Can bo tu phap kiem tra ho so, ghi vao So dang ky khai tu. Thoi han: trong ngay "
            "lam viec hoac ngay lam viec tiep theo.\n"
            "Buoc 4: Nguoi yeu cau nhan Trich luc khai tu; thu lai giay to ca nhan cua nguoi qua doi "
            "theo quy dinh (CCCD, ho chieu, GPLX...)."
        ),
        'conditions': (
            "Dang ky khai tu thuc hien trong vong 15 ngay ke tu ngay nguoi do chet.\n"
            "Nguoi yeu cau la than nhan, nguoi giam ho hoac co trach nhiem theo phap luat.\n"
            "Truong hop chet khong ro ly do phai co bien ban xac nhan chet cua co quan cong an."
        ),
    },
    'dang-ky-thuong-tru': {
        'steps': (
            "Buoc 1: Ca nhan chuan bi ho so gom To khai dang ky cu tru (Mau CT01 ban hanh theo Thong "
            "tu 56/2021/TT-BCA), CCCD / Can cuoc con hieu luc, giay to chung minh cho o hop le (hop "
            "dong thue nha, giay to so huu, xac nhan cua chu ho...).\n"
            "Buoc 2: Nop ho so qua ung dung VNeID (muc uu tien) hoac nop truc tiep tai Cong an cap xa "
            "co tham quyen. Co the nop tai Cong DVC quoc gia.\n"
            "Buoc 3: Can bo Cong an kiem tra, xac minh thong tin; cap nhat vao Co so du lieu dan cu "
            "quoc gia. Thoi han giai quyet: 7 ngay lam viec ke tu ngay nop du ho so.\n"
            "Buoc 4: Ca nhan nhan ket qua qua VNeID hoac tai tru so Cong an cap xa; thong tin thuong "
            "tru duoc the hien tren CCCD / Can cuoc."
        ),
        'conditions': (
            "Co cho o hop le: so huu, thue, muon, o nho voi than nhan co xac nhan chu ho.\n"
            "Khong thuoc truong hop bi cam dang ky thuong tru theo Dieu 24 Luat Cu tru 2020.\n"
            "Nguoi chua thanh nien dang ky theo cha, me hoac nguoi giam ho theo quy dinh."
        ),
    },
    'cap-doi-cccd': {
        'steps': (
            "Buoc 1: Cong dan chuan bi CCCD / CMND cu (ban goc) va xac nhan thong tin ca nhan (neu co "
            "thay doi ho ten, ngay sinh, noi dang ky ho khau).\n"
            "Buoc 2: Den truc tiep Co quan quan ly can cuoc cua Cong an cap tinh / cap huyen / cap xa "
            "duoc uy quyen; hoac dang ky qua ung dung VNeID (thu tuc truc tuyen muc 4).\n"
            "Buoc 3: Can bo cap nhat thong tin sinh trac hoc (anh chan dung, van tay, chu ky dien tu); "
            "ky bien ban thu nhan ho so. Thoi han: 7 ngay lam viec (khu vuc mien nui co the 20 ngay).\n"
            "Buoc 4: Cong dan nhan the Can cuoc moi tai noi da dang ky hoac qua buu chinh; nop lai the "
            "cu / CMND theo yeu cau cua can bo."
        ),
        'conditions': (
            "Cong dan Viet Nam tu du 14 tuoi; tre duoi 6 tuoi cha/me lam thu tuc thay.\n"
            "Thu tuc cap moi ap dung cho nguoi chua co CCCD; cap doi ap dung khi: thay doi noi thuong "
            "tru, thay doi thong tin ca nhan, the bi hong / het han hieu luc.\n"
            "Khong co quyet dinh han che / cam dang ky can cuoc cua co quan co tham quyen."
        ),
    },
    'cap-phieu-lltp': {
        'steps': (
            "Buoc 1: Nguoi co yeu cau chuan bi ho so gom To khai yeu cau cap Phieu ly lich tu phap, "
            "ban sao CCCD / Can cuoc con hieu luc. Xac dinh nop tai So Tu phap (Phieu so 1 cho ca "
            "nhan) hay Trung tam LLTP quoc gia (Phieu so 2 theo yeu cau to chuc).\n"
            "Buoc 2: Nop ho so truc tiep tai Bo phan mot cua So Tu phap tinh Thanh Hoa (34 Dai lo Le "
            "Loi) hoac nop truc tuyen qua Cong DVC quoc gia / tinh; co the nop qua buu chinh.\n"
            "Buoc 3: So Tu phap kiem tra, tra cuu co so du lieu LLTP; xac nhan ket qua. Thoi han: "
            "10 ngay lam viec ke tu ngay nhan du ho so (20 ngay neu phai xac minh nuoc ngoai).\n"
            "Buoc 4: Nguoi yeu cau nhan Phieu LLTP tai noi nop ho so, qua buu chinh hoac tai VNeID "
            "(Phieu LLTP dien tu) theo hinh thuc da chon."
        ),
        'conditions': (
            "Ca nhan co quyen yeu cau cap Phieu LLTP so 1 de su dung theo nhu cau ca nhan.\n"
            "Co quan, to chuc yeu cau cap Phieu so 2 phai co van ban de nghi kem theo uy quyen.\n"
            "Truong hop uy quyen cho nguoi khac: can Giay uy quyen co cong chung va CCCD nguoi duoc "
            "uy quyen."
        ),
    },
    # ── Business ──────────────────────────────────────────────────────────
    'dang-ky-ho-kinh-doanh': {
        'steps': (
            "Buoc 1: Ca nhan / nhom ca nhan / ho gia dinh chuan bi ho so gom Giay de nghi dang ky ho "
            "kinh doanh (Mau Phu luc III-1 Nghi dinh 01/2021/ND-CP), ban sao CCCD cua chu ho va "
            "thanh vien, van ban uy quyen neu nop qua trung gian.\n"
            "Buoc 2: Nop ho so tai Bo phan mot cua UBND cap huyen (Phong Tai chinh - Ke hoach) noi dat "
            "tru so ho kinh doanh; hoac nop truc tuyen qua Cong DVC tinh Thanh Hoa.\n"
            "Buoc 3: Co quan dang ky kiem tra tinh hop le cua ho so. Thoi han cap Giay chung nhan: "
            "3 ngay lam viec ke tu ngay nhan du ho so hop le.\n"
            "Buoc 4: Chu ho kinh doanh nhan Giay chung nhan dang ky ho kinh doanh, tien hanh khac con "
            "dau va lam cac thu tuc thue, mo tai khoan ngan hang (neu can)."
        ),
        'conditions': (
            "Ca nhan tu du 18 tuoi, co nang luc hanh vi dan su day du; khong thuoc doi tuong bi cam "
            "dang ky kinh doanh theo phap luat.\n"
            "Moi ca nhan chi duoc dang ky mot ho kinh doanh trong toan quoc.\n"
            "Nganh nghe kinh doanh khong thuoc danh muc cam; nganh nghe co dieu kien phai dap ung du "
            "dieu kien truoc khi hoat dong.\n"
            "Tru so ho kinh doanh phai hop phap (so huu / thue / muon co xac nhan)."
        ),
    },
    # ── Construction ──────────────────────────────────────────────────────
    'cap-giay-phep-xay-dung': {
        'steps': (
            "Buoc 1: Chu dau tu chuan bi ho so gom Don de nghi cap phep xay dung (theo mau), ban ve "
            "thiet ke kien truc (mat bang, mat dung, mat cat ty le 1/100 hoac 1/200), giay to chung "
            "minh quyen su dung dat (so do / hop dong thue dat).\n"
            "Buoc 2: Nop ho so tai Bo phan mot cua UBND cap huyen (nha o rieng le) hoac So Xay dung "
            "(cong trinh cap tinh, do thi dac biet); hoac nop truc tuyen qua Cong DVC.\n"
            "Buoc 3: Co quan tham dinh kiem tra ho so, xem xet phu hop quy hoach; co the yeu cau "
            "bo sung hoac to chuc thuc dia. Thoi han: 15 ngay lam viec (nha o rieng le).\n"
            "Buoc 4: Chu dau tu nhan Giay phep xay dung; tien hanh xay dung trong vong 12 thang ke "
            "tu ngay cap phep. Ket thuc xay dung phai thong bao hoan cong."
        ),
        'conditions': (
            "Co giay to hop le ve quyen su dung dat tai vi tri xay dung.\n"
            "Cong trinh phu hop quy hoach xay dung / quy hoach do thi da duoc co quan co tham quyen "
            "phe duyet.\n"
            "Thiet ke xay dung dam bao an toan ket cau, PCCC, ve sinh moi truong va kien truc canh quan.\n"
            "Khong xay dung tren dat nong nghiep, dat rung, hanh lang bao ve cong trinh ky thuat."
        ),
    },
    # ── Land ──────────────────────────────────────────────────────────────
    'cap-gcn-quyen-su-dung-dat': {
        'steps': (
            "Buoc 1: Nguoi su dung dat chuan bi ho so gom Don de nghi cap GCN QSDD (Mau 04a/DK), "
            "ban do dia chinh (neu co) hoac so do the dat, cac giay to chung minh nguon goc su dung "
            "dat (hop dong chuyen nhuong, thua ke, tang cho...).\n"
            "Buoc 2: Nop ho so tai Van phong Dang ky dat dai cap huyen hoac Bo phan mot cua UBND cap "
            "huyen; co the nop truc tuyen qua Cong DVC tinh Thanh Hoa.\n"
            "Buoc 3: Van phong DKDD tham tra ho so, do dac ban do dia chinh (neu chua co), trich luc "
            "ban do dia chinh, trinh UBND co tham quyen ky GCN. Thoi han: 30 ngay (dat khong tranh chap).\n"
            "Buoc 4: Nguoi su dung dat nop nghia vu tai chinh (thue, phi, le phi theo quy dinh); "
            "nhan GCN QSDD (So do / So hong) tai noi nop ho so hoac qua buu chinh."
        ),
        'conditions': (
            "Dang su dung dat on dinh, khong co tranh chap, khong thuoc dien thu hoi hoac giai phong "
            "mat bang theo quy hoach.\n"
            "Su dung dat dung muc dich, khong vi pham hanh lang bao ve, khong lan chiem dat cong.\n"
            "Da hoan thanh nghia vu tai chinh ve dat dai (thue su dung dat, phi chuyen muc dich neu co).\n"
            "Nguoi su dung dat la cong dan Viet Nam hoac to chuc theo quy dinh Luat Dat dai 2024."
        ),
    },
    # ── Transport ─────────────────────────────────────────────────────────
    'cap-gplx': {
        'steps': (
            "Buoc 1: Nguoi co nhu cau dang ky hoc lai xe tai co so dao tao duoc cap phep; hoan thanh "
            "chuong trinh dao tao ly thuyet va thuc hanh; dat ky thi sat hach ly thuyet (600 cau) va "
            "sat hach lai xe trong hinh, tren duong (So GTVT tinh to chuc).\n"
            "Buoc 2: Chuan bi ho so gom Giay to ket qua sat hach dat yeu cau, Giay chung nhan suc khoe "
            "con hieu luc (do co so y te duoc phep cap), ban sao CCCD, anh 3x4 cm (2 anh).\n"
            "Buoc 3: Nop ho so tai So Giao thong Van tai tinh Thanh Hoa (09 Dai lo Hung Vuong) hoac "
            "Trung tam sat hach lai xe duoc uy quyen; co the nop truc tuyen qua Cong DVC.\n"
            "Buoc 4: Co quan cap GPLX trong vong 5 ngay lam viec ke tu ngay co ket qua sat hach dat; "
            "nguoi thi nhan GPLX truc tiep hoac qua buu chinh."
        ),
        'conditions': (
            "Du tuoi theo quy dinh: hang B1/B2 tu du 18 tuoi tro len.\n"
            "Du suc khoe theo tieu chuan Thong tu 36/2019/TT-BYT: khong mac benh lam anh huong den "
            "kha nang dieu khien xe, thi luc dat yeu cau.\n"
            "Hoan thanh chuong trinh dao tao tai co so duoc cap phep; dat sat hach theo quy dinh.\n"
            "Khong dang trong thoi gian bi tuoc quyen su dung GPLX hoac cam dieu khien phuong tien."
        ),
    },
}

with app.app_context():
    updated = 0
    skipped = 0
    for proc_id, data in DATA.items():
        steps = data['steps'].strip()
        conds = data.get('conditions', '').strip()
        result = db.session.execute(text("""
            UPDATE public.procedures
            SET steps      = :steps,
                conditions = CASE WHEN :conds = '' THEN conditions ELSE :conds END
            WHERE id = :pid
              AND (steps IS NULL OR steps = '')
        """), {'steps': steps, 'conds': conds or '', 'pid': proc_id})
        if result.rowcount:
            updated += 1
            print(f"  OK  {proc_id}")
        else:
            skipped += 1
            print(f"  --  {proc_id} (da co hoac khong tim thay)")
    db.session.commit()
    print(f"\nKet qua: {updated} cap nhat, {skipped} bo qua.")
