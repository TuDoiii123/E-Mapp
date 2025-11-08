# Hướng dẫn thiết lập Google Maps API

## Bước 1: Lấy Google Maps API Key

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project hiện có
3. Vào **APIs & Services** > **Library**
4. Tìm và bật các API sau:
   - **Maps JavaScript API**
   - **Places API** (tùy chọn, để tìm kiếm địa điểm)

## Bước 2: Tạo API Key

1. Vào **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **API Key**
3. Copy API key vừa tạo

## Bước 3: Cấu hình API Key

Mở file `Frontend/index.html` và thay `YOUR_GOOGLE_MAPS_API_KEY` bằng API key của bạn:

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY&libraries=places"></script>
```

## Bước 4: Giới hạn API Key (Khuyến nghị)

Để bảo mật, nên giới hạn API key:

1. Vào **APIs & Services** > **Credentials**
2. Click vào API key của bạn
3. Trong **Application restrictions**, chọn:
   - **HTTP referrers (web sites)**
   - Thêm domain của bạn (ví dụ: `localhost:5173/*`, `yourdomain.com/*`)
4. Trong **API restrictions**, chọn:
   - **Restrict key**
   - Chọn chỉ **Maps JavaScript API** và **Places API**

## Lưu ý

- API key miễn phí có giới hạn: $200 credit/tháng
- Với giới hạn này, bạn có thể load khoảng 28,000 lần bản đồ/tháng
- Nếu vượt quá, Google sẽ tính phí

## Test API Key

Sau khi cấu hình, khởi động lại frontend và kiểm tra:
- Bản đồ Google Maps sẽ hiển thị thay vì placeholder
- Các marker sẽ xuất hiện trên bản đồ
- Click vào marker để xem thông tin chi tiết

