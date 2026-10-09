# Báo cáo lab: chọn tracker cho 5 video

**Nhóm:** ………………………… **Thành viên:** Đặng Hữu Tâm (2A202602940), …………………………

Detector cố định: `yolo26n.pt`, ảnh 640 px, Re-ID `osnet_x0_25_msmt17`. Không đổi các mục này trong bài nộp chính.

Máy chạy CPU (không GPU). File nộp nằm ở `runs/nop_bai/video_N.txt`, tạo bằng `scripts/run_tracking.py` đủ frame (không `--max-frames`).

## 0. Giả thuyết trước khi chạy (CP1) và baseline (CP2)

Giả thuyết ghi sau khi xem preview, trước khi chạy tracker:

- video_1 (tĩnh, mật độ vừa): ByteTrack có thể đủ; muốn so với BoT-SORT xem Re-ID có tăng IDF1.
- video_2 (đêm, rất đông, nhìn từ cao): người cắt nhau dễ đổi ID; camera tĩnh nên không cần bù chuyển động camera; người nhỏ nên Re-ID ít giúp → so ByteTrack `conf` thấp với StrongSORT.
- video_3 (camera đi bộ, 640×480, người sát camera): hộp dịch nhiều giữa hai frame → dự đoán tracker có Re-ID / bù camera giữ ID tốt hơn ByteTrack.
- video_4 (trung tâm thương mại, sàn bóng và kính phản chiếu): sợ hộp giả trên bóng phản chiếu → có thể cần `conf` cao hơn; camera tiến tới → ưu tiên BoT-SORT.
- video_5 (trên xe bus, rẽ qua giao lộ): cả cảnh trượt ngang khi xe rẽ → dự đoán BoT-SORT (bù chuyển động camera) tốt nhất.

Baseline CP2 (`video_1`, ByteTrack, conf 0.3, iou 0.5, 150 frame): ID 2 và ID 3 (hai phụ nữ áo đỏ / áo tím) giữ đủ 150/150 frame; ID 6 mất 23 frame rồi quay lại đúng ID 6. Lỗi thấy rõ: tracker chỉ ra ~4,3 hộp/frame trong khi nhãn có ~25,7 người/frame — đám người nhỏ ở cuối quảng trường gần như không có hộp; ID 4 mất ở frame 43 khi bị người áo vàng (ID 1) che.

## 1. Cấu hình đã chọn

Mỗi video: tracker bạn nộp, `conf`, `iou`, điều bạn **nhìn thấy** trên video, và một cấu hình đã thử rồi loại.

| Video | Tracker | conf | iou | Quan sát khi xem video | Đã thử nhưng loại |
|---|---|---|---|---|---|
| video_1 (quảng trường, tĩnh, ban ngày) | botsort | 0.3 | 0.7 | Người đi gần camera giữ ID suốt đoạn dài; lỗi chính là bỏ sót người nhỏ ở xa (detector chỉ bắt ~22% hộp nhãn, độ chính xác hộp 87%). | bytetrack 0.3/0.5 (HOTA 26,9 — kém nhất); botsort 0.5/0.5 (HOTA 27,2, bỏ sót thêm người); deepocsort 0.3/0.5 (IDSW 51, nhiều nhất) |
| video_2 (phố đêm, tĩnh, rất đông) | bytetrack | 0.15 | 0.5 | Người dưới cột đèn chói giữ ID 3 từ frame 400 đến 700; không thấy hộp giả trên cọc giao thông hay mặt đường. Đám đông nhỏ ở cuối phố không tracker nào bắt được. | bytetrack 0.5/0.5 (cùng người dưới đèn đổi ID 69 → 115, track đứt 282 lần); ocsort / strongsort / deepocsort 0.3/0.5 (76–79 ID, track đứt 318–339 lần) |
| video_3 (camera di động, ảnh nhỏ) | bytetrack | 0.15 | 0.5 | Khó với mọi tracker: fps thấp, người sát camera che kín nhau. Người áo len đỏ giữ ID suốt đoạn frame 540–560; nhưng khi người quàng khăn hồng bị che, ID của cô chuyển sang người áo đen đi ngược chiều (cả ByteTrack lẫn StrongSORT cùng mắc). ByteTrack ít ID và ít track vụn nhất. | strongsort 0.3/0.5 (giữ được ID bà áo xám ở frame 300–312 mà ByteTrack hoán đổi, nhưng tổng 160 ID, 74 track < 10 frame); strongsort 0.15/0.5 (218 ID, 119 track vụn); botsort / deepocsort 0.3/0.5 (167–169 ID) |
| video_4 (trong nhà, camera di chuyển) | bytetrack | 0.15 | 0.5 | Không thấy hộp giả trên sàn bóng hay kính phản chiếu, kể cả ở conf 0.15. Người áo vàng giữ ID 32 khi tiến sát camera (frame 280–320). conf 0.15 bắt thêm người cầm túi trắng (ID 48, frame 600) mà conf 0.3 bỏ sót. | botsort 0.3/0.5 (73 ID, track đứt 65 lần); ocsort 0.3/0.5 (79 ID, 122 lần); bytetrack 0.5/0.5 (64 ID, 63 lần) |
| video_5 (trên xe bus, giao lộ đông) | botsort | 0.3 | 0.5 | Khi xe rẽ (frame 420–440) cả khung hình trượt ngang; BoT-SORT giữ ID 125 cho người phụ nữ đeo kính dù cô trượt từ giữa ra mép trái, và vẫn có hộp cho người trên vỉa hè (ID 123, nhóm cạnh biển "Breakfast"). | bytetrack 0.15/0.5 và 0.3/0.5: ít track đứt trên giấy nhưng chỉ ~2,8 hộp/frame — bỏ sót hẳn những người BoT-SORT bám được ở đoạn xe rẽ |

## 2. Số liệu video_1

Bảng do `scripts/evaluate_practice.py` in ra cho `runs/nop_bai/video_1.txt` (botsort, conf 0.3, iou 0.7):

```
HOTA: nhom_video1-pedestrian       HOTA      DetA      AssA      DetRe     DetPr     AssRe     AssPr     LocA      OWTA      HOTA(0)   LocA(0)   HOTALocA(0)
video_1                            29.969    18.408    49.061    19.176    74.385    52.38     80.959    83.019    30.624    37.181    76.409    28.409

CLEAR: nhom_video1-pedestrian      MOTA      MOTP      MODA      CLR_Re    CLR_Pr    MTR       PTR       MLR       sMOTA     CLR_TP    CLR_FN    CLR_FP    IDSW      MT        PT        ML        Frag
video_1                            19.025    80.817    19.202    22.491    87.244    14.516    17.742    67.742    14.71     4179      14402     611       33        9         11        42        105

Identity: nhom_video1-pedestrian   IDF1      IDR       IDP       IDTP      IDFN      IDFP
video_1                            29.703    18.68     72.463    3471      15110     1319

Count: nhom_video1-pedestrian      Dets      GT_Dets   IDs       GT_IDs
video_1                            4790      18581     55        62
```

Các cấu hình đã thử trên `video_1` (đủ 600 frame, chấm bằng TrackEval):

| Cấu hình (tracker conf/iou) | HOTA | MOTA | IDF1 | IDSW |
|---|---|---|---|---|
| bytetrack 0.3/0.5 | 26,9 | 17,3 | 25,7 | 12 |
| ocsort 0.3/0.5 | 27,5 | 19,8 | 28,7 | 42 |
| botsort 0.3/0.5 | 29,5 | 19,8 | 29,4 | 25 |
| strongsort 0.3/0.5 | 28,7 | 19,7 | 29,9 | 41 |
| deepocsort 0.3/0.5 | 27,4 | 19,8 | 27,8 | 51 |
| bytetrack 0.15/0.5 | 27,3 | 18,3 | 27,0 | 13 |
| bytetrack 0.5/0.5 | 25,3 | 15,9 | 23,4 | 14 |
| botsort 0.15/0.5 | 29,3 | 20,7 | 29,6 | 27 |
| botsort 0.5/0.5 | 27,2 | 15,3 | 24,6 | 10 |
| botsort 0.3/0.4 | 29,3 | 19,5 | 29,8 | 19 |
| **botsort 0.3/0.7 (nộp)** | **30,0** | 19,0 | 29,7 | 33 |
| botsort 0.15/0.7 | 29,7 | 20,3 | 29,9 | 39 |

`video_2` đến `video_5` không có nhãn trong gói lab. Không điền số cho các video đó.

Với video không nhãn, nhóm so cấu hình bằng file kết quả (số ID, số track ngắn hơn 10 frame, số lần một track bị đứt rồi nối lại) rồi xem frame có vẽ ID. Đây chỉ là đếm trên output, không phải HOTA / MOTA / IDF1. Số liệu từng lượt thử nằm trong `runs/thu/ket_qua.jsonl`.

## 3. Phân tích

**video_1 — BoT-SORT thắng nhờ Re-ID, nhưng trần là detector.** Camera tĩnh, ban ngày, mật độ vừa. BoT-SORT (Re-ID + chuyển động) có HOTA 29,5–30,0, cao hơn ByteTrack (26,9) chủ yếu ở phần giữ danh tính (AssA 49 so với 48 và IDF1 29,7 so với 25,7). Tuy vậy cả năm tracker đều có DetA chỉ 15–19: detector `yolo26n` ở 640 px chỉ bắt được ~22% hộp nhãn (CLR_Re 22,5%) vì 42% người trong nhãn cao dưới 100 px. Hạ `conf` xuống 0.15 tăng MOTA (ít bỏ sót hơn) nhưng tăng IDSW; nâng lên 0.5 thì giảm IDSW nhưng mất người. Lỗi lớn nhất của bài này là "bỏ sót", không phải "đổi ID".

**video_2 — cảnh tĩnh, đông, ban đêm: ByteTrack với conf thấp hợp hơn tracker có Re-ID.** Camera đứng yên nên mô hình chuyển động Kalman dự đoán tốt; người nhỏ và ánh sáng đèn làm đặc trưng ngoại hình kém tin cậy. Thấy trên video: người đứng dưới cột đèn chói giữ ID 3 từ frame 400 đến 700 khi `conf` 0.15, còn ở `conf` 0.5 người đó đổi ID 69 → 115 vì hộp điểm thấp ở vùng chói bị loại. Đây đúng là ý tưởng của ByteTrack: không vứt hộp điểm thấp mà dùng nó để nối track cũ. Các tracker có Re-ID (StrongSORT, DeepOCSORT) tạo nhiều ID hơn và track bị đứt nhiều hơn hẳn (318–339 lần so với 13).

**video_5 — camera trên xe bus: BoT-SORT nhờ bù chuyển động camera.** Khi xe rẽ, mọi người trong ảnh đồng loạt trượt ngang dù họ đứng yên; Kalman của ByteTrack hiểu đó là người đang chạy và đoán sai vị trí. BoT-SORT ước lượng chuyển động của cả khung hình (GMC) rồi trừ đi trước khi ghép, nên người phụ nữ đeo kính giữ ID 125 dù trượt từ giữa ra mép trái trong 20 frame. Số "track đứt" của ByteTrack thấp hơn chỉ vì nó bám ít người hơn (~2,8 so với 4,1 hộp/frame) — phải xem video mới thấy điều này.

**Giả thuyết bị bác.** Ở video_4 nhóm đoán bóng phản chiếu trên sàn và kính sẽ tạo hộp giả nên cần `conf` cao; thực tế detector không nhầm bóng thành người, và `conf` 0.15 còn bắt thêm người thật. Camera tiến chậm, mọi người đi cùng chiều nên chuyển động khá tuyến tính, ByteTrack đủ dùng. Ở video_3 nhóm đoán Re-ID sẽ thắng; thực tế StrongSORT giữ được một trường hợp mà ByteTrack hoán đổi ID, nhưng tổng thể lại tạo nhiều ID vụn hơn — ảnh 640×480, người cắt ngang sát camera khiến crop ngoại hình bị mờ và che khuất, Re-ID không đủ tin cậy.

## 4. Nếu có thêm thời gian

Nhóm sẽ thử quét `conf` / `iou` cho BoT-SORT trên video_5 và quét `iou` ở video_2–video_4 (máy chỉ có CPU nên đã bớt lượt quét ở các video không nhãn). Ngoài ra muốn xem kỹ các frame đổi ID ở video_3 để biết lỗi do che khuất hay do fps thấp, và thử tăng `track_buffer` của tracker (phần mở rộng, không thuộc bài nộp chính).
