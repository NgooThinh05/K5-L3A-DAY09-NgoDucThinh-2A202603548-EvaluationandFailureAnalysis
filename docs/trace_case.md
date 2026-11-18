# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi nhóm 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11` (lỗi tương tự xuất hiện ở `swarm C-002@55`) |
| Triệu chứng | Grader Lab 8 `FAIL (status resolved != denied)`. Reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`, ledger ghi `refund_vnd=20000`, `refund_count=1`, trong khi nhãn chuẩn là `0`, `0`, `denied`. |
| Bước sai đầu tiên | Event `3`: `model_override` — `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event `1` (`handoff`) giao đúng `task: check_applicable_policy` với `facts: {}`; event `2` (`investigator` / `lookup_order`) trả về đúng dữ liệu DB của `O-202` (`delay_days=2`). Ngay ở bước `3`, agent lấy `5` ngày từ ticket đè lên giá trị DB `2`, kéo theo `quote` (bước 4) và `issue_refund` (bước 6) đều sai. |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Trên `fixed C-002@11`: không có event `model_override`; bước `3` là `quote` với `amount_vnd: 0, reason: "no_entitlement"`, bước `4` `reply` từ chối đúng nhãn (`denied`, `refund_vnd=0`). |
| Regression test | `src/tests/test_lab9_trace_case.py::test_seeded_regression_c002_fails_with_model_override` (kết hợp grader `DbFactKept` và item `E-002` trong `eval_set_v1.jsonl`); đã thấy FAIL trên `seeded_regression` và PASS trên `fixed`. |
| Chưa chắc chắn | MockLLM bỏ qua prompt thực tế, nên không kết luận được liệu prompt engineering thuần túy trên LLM thật có đủ chặn `ticket_trust` nếu không khóa ở code tầng tool/orchestration. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
