# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Đạt (`TP=24, FP=4, FN=6, TN=66`; fail rate quan sát `0.28` → Rogan-Gladen `0.30`) | **dùng** (làm tín hiệu phụ cho tone, sau khi siết rubric) |
| helpful | 100 | 0.375 | 1.000 | 0.300 | **Không đạt** (`TP=9, FP=0, FN=21, TN=70`; κ `< 0.6` và R `< 0.7`; fail rate quan sát `0.09` → Rogan-Gladen `0.30`) | **loại** (không được dùng làm gate) |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & hành động sửa rubric |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`) | `PASS` | `FAIL` | Người | Reply *"Em đã hoàn tiền cho anh rồi nha..."*: xưng `em` + `nha` quá suồng sã. Sửa rubric: liệt kê rõ từ ngữ cấm (`em`, `nha`, `bạn`, `nhé`), bắt buộc `anh/chị` + `LogiX`. |
| 2 | `H-029` (`tone_ok`) | `PASS` | `FAIL` | Người | Reply *"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."*: có `Dạ, vui lòng` nhưng mang giọng ra lệnh (`không cần nhắn thêm`). Sửa rubric: chấm FAIL các câu đuổi khéo/cấm khách phản hồi. |
| 3 | `H-042` (`tone_ok`) | `FAIL` | `PASS` | Người | Reply *"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."* ngắn gọn, lịch sự, đủ thông tin nhưng judge phạt vì thiếu xin lỗi. Sửa rubric: không yêu cầu câu xin lỗi với thông báo kết quả rõ ràng. |
| 4 | `H-051` (`tone_ok`) | `FAIL` | `PASS` | Người | Reply *"Dạ, LogiX đã refund 90.000đ..."*: CS LogiX cho phép thuật ngữ `refund`, judge phạt nhầm do có tiếng Anh. Sửa rubric: whitelist thuật ngữ `refund`, `order`, `claim`. |
| 5 | `H-070` (`tone_ok`) | `PASS` | `FAIL` | Người | Reply có emoji `😂😂` trong ngữ cảnh khiếu nại. Sửa rubric: cấm tuyệt đối emoji trong mọi phản hồi CSKH. |
| 6 | `H-081` (`tone_ok`) | `FAIL` | `PASS` | Judge | Reply *"Dạ, đơn O-107 chưa đủ điều kiện..."* — nhãn người đánh sai do đọc nhầm ticket; giữ phán quyết judge và sửa lại gold label. |
| 7 | `HL-016` (`helpful`) | `PASS` | `FAIL` | Người | Reply xin lỗi rất dài dòng và lịch sự, nhưng nói hoàn `55.000đ` trong khi ledger chỉ ghi `35.000đ` (`FM-08`). Judge text-only bị đánh lừa bởi verbosity + câu xin lỗi. |
| 8 | `HL-047` (`helpful`) | `PASS` | `FAIL` | Người | Reply *"Ok bạn, đơn O-515 xử lý rồi nhé."* thiếu thông tin kết quả cụ thể và sai xưng hô, nhưng judge vẫn cho `PASS`. |

## Kết luận
- **Tiêu chí bị loại (`helpful`):** `judge_helpful` có `TP=9, FP=0, FN=21, TN=70` → `κ = 0.375 < 0.6` và `Recall = 0.300 < 0.7`. Judge chỉ đọc văn bản `reply` nên bị đánh lừa bởi các câu xin lỗi dài dòng (verbosity bias) và **bỏ sót 21/30 ca lỗi (`FN = 21`)**, đặc biệt là các ca báo sai số tiền so với ledger (`HL-015`, `HL-016`, `HL-020`, `HL-028`, ...). Điều này kéo tỉ lệ lỗi quan sát xuống giả tạo chỉ còn `9%`, trong khi tỉ lệ lỗi thực sau hiệu chỉnh Rogan-Gladen là `30%`. Vì vậy tuyệt đối không dùng `judge_helpful` làm CI gate; việc đối chiếu số tiền/trạng thái với ledger phải chấm bằng **code grader** (`ReplyMatchesLedger`, `RefundAmountCorrect`).
- **Tiêu chí đạt (`tone_ok`):** `judge_tone` đạt toàn bộ ngưỡng (`κ = 0.757 ≥ 0.6`, `P = 0.857 ≥ 0.8`, `R = 0.800 ≥ 0.7`) và có thể dùng làm metric kiểm tra văn phong sau khi cập nhật rubric (xưng hô, cấm emoji, whitelist `refund`, không ép xin lỗi máy móc).
- **Rủi ro còn lại:** Judge chỉ được hiệu chuẩn trên dữ liệu replay công khai (`100` mẫu CSV); cần gán nhãn người trên một tập held-out mới (và bổ sung cặp nhãn mới sau khi sửa rubric) để tránh quá khớp vào bộ public.
