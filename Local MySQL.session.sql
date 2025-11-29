-- =========================================
-- 0. TẠO DATABASE CHO CHỨC NĂNG BẢN ĐỒ HÀNG CHỜ
-- =========================================
CREATE DATABASE IF NOT EXISTS emapp_queue
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE emapp_queue;

-- =========================================
-- 1. BẢNG offices - DANH MỤC CƠ QUAN HÀNH CHÍNH
-- =========================================
CREATE TABLE IF NOT EXISTS offices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,     -- Tên cơ quan
    address     VARCHAR(255),              -- Địa chỉ text
    lat         DOUBLE NOT NULL,           -- Vĩ độ
    lng         DOUBLE NOT NULL,           -- Kinh độ
    type        VARCHAR(50),               -- Loại: HCC_QUAN, UBND_PHUONG,...
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 2. BẢNG service_types - LOẠI DỊCH VỤ CÔNG
-- =========================================
CREATE TABLE IF NOT EXISTS service_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code        VARCHAR(50) NOT NULL UNIQUE,   -- Mã: CCCD, BIRTH, HOUSEHOLD,...
    name        VARCHAR(255) NOT NULL         -- Tên hiển thị
);

-- =========================================
-- 3. BẢNG citizens - NGƯỜI DÂN (CÓ THỂ ẨN DANH)
-- =========================================
CREATE TABLE IF NOT EXISTS citizens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone       VARCHAR(30),
    email       VARCHAR(100),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 4. BẢNG visits - LƯỢT CHECK-IN / CHECK-OUT
-- =========================================
CREATE TABLE IF NOT EXISTS visits (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    citizen_id              INT NULL,              -- Có thể null nếu ẩn danh
    office_id               INT NOT NULL,
    service_type_id         INT NULL,
    check_in_time           DATETIME NOT NULL,
    check_out_time          DATETIME NULL,
    waiting_duration_min    INT NULL,             -- phút = check_out - check_in
    source                  VARCHAR(20) NOT NULL, -- 'CITIZEN_APP' / 'OFFICIAL_API'
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_visits_citizen
        FOREIGN KEY (citizen_id) REFERENCES citizens(id),

    CONSTRAINT fk_visits_office
        FOREIGN KEY (office_id) REFERENCES offices(id),

    CONSTRAINT fk_visits_service_type
        FOREIGN KEY (service_type_id) REFERENCES service_types(id)
);

-- =========================================
-- 5. BẢNG office_queue_snapshots - SNAPSHOT HÀNG CHỜ
-- =========================================
CREATE TABLE IF NOT EXISTS office_queue_snapshots (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    office_id               INT NOT NULL,
    service_type_id         INT NULL,
    current_waiting_count   INT NOT NULL,         -- số người đang chờ
    avg_waiting_minutes     INT NULL,             -- thời gian chờ TB
    status_level            VARCHAR(10) NOT NULL, -- 'LOW' / 'MEDIUM' / 'HIGH'
    last_updated_at         DATETIME NOT NULL,
    source                  VARCHAR(20) NOT NULL, -- 'CROWDSOURCE' / 'OFFICIAL',

    CONSTRAINT fk_snapshots_office
        FOREIGN KEY (office_id) REFERENCES offices(id),
 
    CONSTRAINT fk_snapshots_service_type
        FOREIGN KEY (service_type_id) REFERENCES service_types(id)
);
