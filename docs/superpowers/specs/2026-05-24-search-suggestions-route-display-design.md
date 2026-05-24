# Design: Smart Search Suggestions + Route Display on Map

**Date:** 2026-05-24  
**Status:** Approved  
**Scope:** MapScreen — tìm kiếm gợi ý cơ quan + hiển thị đường đi trên bản đồ

---

## 1. Tổng quan

Hai tính năng bổ sung cho `MapScreen.tsx`:

1. **Smart Search Suggestions** — khi gõ vào ô tìm kiếm, dropdown gợi ý hiện danh sách cơ quan nhà nước từ DB (kèm badge hàng chờ), thay thế OSM Nominatim autocomplete hiện tại.
2. **Route Display on MAP** — khi ấn "Chỉ đường" và chọn phương tiện, vẽ polyline đường đi màu sắc rõ ràng trên bản đồ kèm floating badge thời gian/khoảng cách.

---

## 2. Feature 1: Smart Search Suggestions

### Hành vi
- User gõ ≥ 2 ký tự → debounce 300ms → gọi `servicesAPI.search(q, lat, lng)`
- Dropdown hiện tối đa 8 cơ quan khớp tên/địa chỉ từ toàn bộ DB (không giới hạn radius)
- Mỗi item hiện: icon 🏛, tên cơ quan, địa chỉ, khoảng cách (nếu có vị trí), badge hàng chờ
- Badge hàng chờ: 🟢 Vắng (0–5) · 🟡 TB (6–15) · 🔴 Đông (>15) — lấy từ `queueData`
- Click item → `handleSelectOffice(office)` → mở sidebar detail (flow hiện tại)
- Nếu cơ quan ngoài `offices[]` (ngoài radius) → thêm vào `offices` state tạm + pan map

### Thay đổi code
| File | Thay đổi |
|------|----------|
| `MapScreen.tsx` | `handleSearchInput`: thay `mapAPI.autocomplete()` → `servicesAPI.search()` |
| `MapScreen.tsx` | State `predictions: AutocompletePrediction[]` → `suggestions: PublicService[]` |
| `MapScreen.tsx` | `selectPrediction(pred)` → `selectSuggestion(office: PublicService)` |
| `MapScreen.tsx` | Dropdown UI: render `PublicService[]` với badge queue từ `queueData` |
| `servicesApi.ts` | Không cần thay đổi — `servicesAPI.search()` đã có |

### Backend
- `GET /api/services/search?q=&lat=&lng=&limit=8` — **đã có sẵn** tại `services_routes.py:76`
- Không cần thêm endpoint mới

---

## 3. Feature 2: Route Display on MAP

### Hành vi
- Ấn "Chỉ đường" trong detail panel → `enterDirectionsMode(office)` → sidebar chuyển sang directions panel
- `fetchDirections(office, mode)` → gọi `GET /api/map/directions` → trả `coordinates[]` + `steps[]`
- Map vẽ polyline 4 lớp (shadow + viền trắng + màu chính + nét đứt động)
- **Màu route theo phương tiện:** 🔵 `#3B82F6` driving · 🟢 `#10b981` walking · 🟡 `#f59e0b` cycling
- Floating badge trên bản đồ: `🚗 8 phút · 2.3 km` (absolute position, cập nhật khi đổi mode)
- Chuyển phương tiện → `fetchDirections()` lại → route màu mới render ngay
- Click bước trong sidebar → `mapInstance.setView(step.location, 17)` → map pan đến điểm rẽ
- Marker A (xanh lá) điểm xuất phát · Marker B (đỏ) điểm đến

### Thay đổi code
| File | Thay đổi |
|------|----------|
| `MapScreen.tsx` | Thêm state `routeInfoBadge: {duration, distance, mode} | null` |
| `MapScreen.tsx` | `useEffect([directionsInfo, dirMode])` — đã render polyline, thêm floating badge |
| `MapScreen.tsx` | Badge render trên `<div className="flex-1 relative">` (phần map) |
| `MapScreen.tsx` | Test & verify OSRM trả `coordinates` đúng — fallback nếu rỗng |

### Backend
- `GET /api/map/directions` — **đã có sẵn**, trả `coordinates` + `steps` + `duration` + `distance`
- Không cần thêm endpoint mới

---

## 4. Không thay đổi
- Logic filter bán kính (`radius`, `selectedCategory`) — giữ nguyên cho list bên dưới
- `handleSelectOffice()` — giữ nguyên toàn bộ
- Sidebar detail panel layout — giữ nguyên
- Smart Route tab (Gợi ý AI) — không đụng tới

---

## 5. Files cần sửa
1. `Frontend/src/components/MapScreen.tsx` — thay đổi chính
2. `Frontend/src/services/servicesApi.ts` — kiểm tra type `SearchServicesResponse`

---

## 6. Acceptance Criteria
- [ ] Gõ "UBND" → dropdown hiện ≥ 1 cơ quan từ DB trong <500ms
- [ ] Badge hàng chờ hiển thị đúng màu theo `queueData`
- [ ] Click gợi ý → sidebar detail mở đúng cơ quan, map pan đến vị trí
- [ ] Cơ quan ngoài radius vẫn tìm được và hiện trên map
- [ ] Ấn "Chỉ đường" → polyline xuất hiện trên map
- [ ] Chuyển xe/bộ/đạp → route đổi màu ngay lập tức
- [ ] Floating badge trên map hiện đúng thời gian & khoảng cách
- [ ] Click bước hướng dẫn → map pan đến điểm rẽ tương ứng
