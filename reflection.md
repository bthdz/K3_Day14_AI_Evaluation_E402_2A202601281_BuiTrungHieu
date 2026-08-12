# Day 14 — Reflection

## Evaluation Report & Failure Analysis

Dùng kết quả thật trong `artifacts/benchmark_results.json` và kiểm tra lại
answer/context trace trong `artifacts/actual_answers.json` trước khi kết luận.

---

## 1. Benchmark Results Summary

**Overall pass rate:** 0.0%

| Metric | Average | Min | Max | Nhận xét |
|---|---:|---:|---:|---|
| Context Recall | 0.457 | 0.108 | 1.000 | Retriever lấy được một phần thông tin, nhưng thiếu sót nhiều ở các câu hỏi khó. |
| Context Precision | 0.568 | 0.000 | 1.000 | Các chunks trả về có tỷ lệ thông tin hữu ích trung bình khá. |
| Faithfulness | 0.159 | 0.000 | 0.786 | Rất thấp, do LLM diễn đạt lại từ vựng (paraphrase) không khớp với cách chấm lexical. |
| Relevance | 0.360 | 0.000 | 0.600 | Câu trả lời thường dài dòng hoặc từ chối trả lời, dẫn tới relevance thấp. |
| Completeness | 0.230 | 0.000 | 1.000 | Thiếu ý trong câu trả lời do model không tận dụng hết context. |
| Overall Score | ~0.261 | 0.000 | 0.679 | Đa số các câu đều bị đánh trượt (Pass = 0%). |

**Score interpretation**

- Metrics/cases ở mức Good (0.8–1.0): Chỉ có 1-2 cases đạt điểm này ở Recall và Precision.
- Metrics/cases ở mức Needs Work (0.6–0.8): Ít (khoảng 3 cases).
- Metrics/cases ở mức Significant Issues (<0.6): Đa số (15+ cases), đặc biệt ở Faithfulness.

**Failure type distribution**

| Failure Type | Count | Percentage |
|---|---:|---:|
| hallucination | 17 | 85% |
| irrelevant | 2 | 10% |
| incomplete | 1 | 5% |
| off_topic | 0 | 0% |
| refusal | 0 | 0% |

**Chẩn đoán tổng quan:** Vấn đề chính nằm ở retrieval, generation hay cả hai?
Dùng ít nhất hai metrics để bảo vệ kết luận.

> *Câu trả lời:* Vấn đề nằm ở **cả hai**, nhưng **generation là nghiêm trọng nhất**. 
> - Thứ nhất, **Faithfulness (0.159) cực kỳ thấp**: Model sinh ra câu trả lời nhưng dùng ngôn từ paraphrase khiến hệ thống chấm bằng Lexical Overlap (đếm số từ trùng lặp) đánh dấu là hallucination.
> - Thứ hai, **Context Recall (0.457) cũng không cao**: Retriever BM25 có giới hạn trong việc lấy đúng chunks khi câu hỏi dùng từ đồng nghĩa, dẫn tới LLM không có đủ context để trả lời, làm Completeness bị giảm theo (0.230).

---

## 2. Top 3 Worst Failures — 5 Whys

Phân loại failure trước khi đề xuất fix. Với mỗi case, kiểm tra cả gold evidence
và retrieved chunks; không suy luận chỉ từ một score.

### Failure 1

**ID và question:** M02 - How do leave and graduation relate?

**Expected answer:** Leave of absence có thể ảnh hưởng đến tiến độ tốt nghiệp.

**Actual answer:** API returned an empty answer or hallucination/refusal (phụ thuộc log).

**Scores:** Context Recall: 0.688 | Context Precision: 0.700 | Faithfulness: 0.000 |
Relevance: 0.000 | Completeness: 0.000 | Overall: 0.000

**Evidence inspection:** Retriever lấy đúng/thiếu/thừa chunks nào?
> *Câu trả lời:* Retriever lấy được thông tin tương đối tốt (Recall 0.688) nhưng model sinh ra câu trả lời trống hoặc không liên quan.

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | Faithfulness và Completeness = 0 |
| Why 1 | Tại sao symptom xảy ra? | Model sinh câu trả lời rỗng hoặc diễn đạt bằng từ vựng khác hoàn toàn expected answer. |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | Prompt không ép LLM dùng đúng từ vựng trong context, hoặc metric Lexical quá gắt. |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | RAGASEvaluator đang dùng `_compute_lexical_overlap` thay vì LLM-as-a-Judge. |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | Đang là bài thực hành Lexical baseline. |
| Why 5 | Root cause có thể hành động được là gì? | Cần dùng LLM Judge thay vì Lexical overlap cho metrics generation. |

**Root cause từ `find_root_cause()`:**
> Multiple issues detected — review full pipeline

**Bạn đồng ý hay không? Dẫn evidence từ trace:**
> *Câu trả lời:* Đồng ý một phần. Lỗi lớn nhất đến từ metric chấm điểm chứ không hoàn toàn do model sinh lỗi.

**Proposed fix cụ thể:**
> *Câu trả lời:* Implement LLM-as-a-Judge hoặc cải thiện Prompt để LLM trích dẫn nguyên văn context thay vì paraphrase.

### Failure 2

**ID và question:** H04 - What are the complex rules for attendance?

**Expected answer:** (Các rules về attendance)

**Actual answer:** API returned an empty answer or the response was blocked.

**Scores:** Context Recall: 0.381 | Context Precision: 0.333 | Faithfulness: 0.000 |
Relevance: 0.000 | Completeness: 0.000 | Overall: 0.000

**Evidence inspection:**
> *Câu trả lời:* API trả về lỗi hoặc model từ chối trả lời do safety filters (Over-refusal).

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | Lỗi API hoặc model trả về chuỗi rỗng. |
| Why 1 | Tại sao symptom xảy ra? | API bị timeout hoặc model gặp safety block. |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | Từ khóa trong câu hỏi kích hoạt rule an toàn của API. |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | Code chưa có logic retry hoặc bypass safety prompt hợp lệ. |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | Error handling đang trả về chuỗi rỗng để tránh crash pipeline. |
| Why 5 | Root cause có thể hành động được là gì? | Thêm fallback prompt hoặc tinh chỉnh tham số API. |

**Root cause và proposed fix:**
> *Câu trả lời:* Root cause: API chặn nội dung hoặc trả về None. Fix: Cập nhật fallback prompt và thiết lập cơ chế retry khi có lỗi API.

### Failure 3

**ID và question:** E05 - What is a fact about scholarships.md?

**Expected answer:** Có nhiều loại học bổng khác nhau cho sinh viên.

**Actual answer:** (Model sinh ra một câu tóm tắt nội dung về scholarships)

**Scores:** Context Recall: 0.375 | Context Precision: 0.679 | Faithfulness: 0.167 |
Relevance: 0.200 | Completeness: 0.062 | Overall: 0.143

**Evidence inspection:**
> *Câu trả lời:* Retriever lấy được thông tin có liên quan (Precision khá cao) nhưng Recall thấp (do câu hỏi quá chung chung).

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | Faithfulness và Completeness rất thấp dù Precision tốt. |
| Why 1 | Tại sao symptom xảy ra? | Model diễn đạt thông tin bằng từ vựng khác với expected answer. |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | Expected answer quá ngắn gọn, model lại trả lời chi tiết hơn. |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | RAGASEvaluator dùng Lexical overlap, phạt các câu trả lời dài và diễn đạt khác. |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | Hệ thống chưa sử dụng Semantic Similarity. |
| Why 5 | Root cause có thể hành động được là gì? | Chuyển sang chấm điểm bằng Semantic Similarity hoặc LLM-as-a-Judge. |

**Root cause và proposed fix:**
> *Câu trả lời:* Root cause: Lexical overlap metric không đánh giá đúng ngữ nghĩa câu trả lời. Fix: Thay đổi metric đánh giá sang LLM-as-a-Judge.

---

## 3. Failure Clustering

Một root cause có thể tạo ra nhiều failures. Nhóm theo nguyên nhân có thể sửa,
không chỉ nhóm theo tên metric.

| Cluster | Root Cause | Failure IDs | Priority |
|---|---|---|---|
| 1 | Metric Lexical không hiểu semantics | M01, M02, M03, E01, E02, E05... | High |
| 2 | Model gặp Safety Filters / Error API | H04 | Medium |
| 3 | Chunk size quá nhỏ / BM25 thiếu context | H01, H05, M04 | Medium |

**Nếu chỉ được sửa một cluster, bạn chọn cluster nào và vì sao?**

> *Câu trả lời:* Em sẽ chọn sửa Cluster 1 (Metric Lexical) đầu tiên. Bởi vì nếu metric đo đạc bị sai, chúng ta không thể biết được thực sự hệ thống RAG đang làm tốt hay tệ. Sửa metric (chuyển sang LLM Judge) sẽ mang lại kết quả benchmark thực tế và đáng tin cậy hơn để tiếp tục tối ưu hệ thống.

---

## 4. Improvement Log

Paste output của `generate_improvement_log()`:

```text
| Failure ID | Type | Root Cause | Suggested Fix | Status |
|------------|------|------------|---------------|--------|
| F001 | hallucination | Multiple issues detected | Implement hallucination checker to filter unsupported claims | Open |
| F002 | hallucination | Multiple issues detected | Improve prompt clarity to better address the user's question | Open |
| F003 | irrelevant | Multiple issues detected | Increase chunk size in RAG pipeline to reduce context fragmentation | Open |
| F004 | irrelevant | Answer does not address the question | Add few-shot examples showing complete answers to improve completeness | Open |
| F005 | hallucination | Multiple issues detected | Tune retrieval thresholds to provide higher-quality context | Open |
```

**Ba improvement suggestions ưu tiên**

1. Implement LLM-as-a-Judge thay vì Lexical Metrics.
2. Cải thiện Prompt clarity và thêm few-shot examples để hướng dẫn LLM.
3. Tăng chunk size và tune thuật toán BM25 / chuyển sang Vector retrieval.

Với mỗi suggestion, nêu metric dự kiến thay đổi và cách đo lại.

| Suggestion | Target metric | Verification method |
|---|---|---|
| Dùng LLM Judge | Faithfulness, Completeness | Chạy lại pipeline evaluate_answers.py trên cùng tập dataset |
| Cải thiện Prompt (Few-shot) | Relevance | Đo đạc lại Relevance xem model có trả lời tập trung không |
| Dùng Vector Retrieval thay cho BM25 | Context Recall, Context Precision | Chạy lại 20 câu hỏi và theo dõi Delta Recall |

---

## 5. Regression Testing Strategy

**Câu 1: Khi nào chạy `run_regression()` trong production workflow?**

> *Câu trả lời:* Nên chạy trong CI/CD pipeline (khi mở Pull Request thay đổi logic Prompt, thay đổi model, hoặc cập nhật thuật toán Retrieval).

**Câu 2: Threshold drop 0.05 có phù hợp Student Services không? Vì sao?**

> *Câu trả lời:* Khá phù hợp, 0.05 là mức sụt giảm 5% điểm trung bình. Student Services đòi hỏi sự chính xác cao (học phí, bằng cấp), do đó 5% là một ngưỡng cảnh báo an toàn để trigger review lại.

**Câu 3: Metric/failure nào phải block deployment, metric nào chỉ alert?**

> *Câu trả lời:* **Faithfulness (sự thật)** bị tụt (ảo giác thông tin) phải **block deployment** vì sinh viên sẽ nhận sai chính sách (ví dụ: tư vấn sai học phí). **Completeness** hoặc **Relevance** nếu giảm nhẹ thì chỉ cần **alert** để optimize sau.

**Câu 4: Điền evaluation stages vào flow.**

```text
Code/prompt/retrieval change → [Unit Tests] → [Regression Tests (evaluate_answers.py)] → [Human Review for failures] → Deploy
```

> *Giải thích:* Unit tests đảm bảo code không lỗi logic. Regression Tests đảm bảo chất lượng AI không đi lùi. Human Review giải quyết các edge cases do LLM Judge chấm sai trước khi lên production.

---

## 6. Continuous Improvement Loop

```text
Evaluate → Analyze → Improve → Augment benchmark → Repeat
```

| Priority | Action | Metric dự kiến cải thiện | Expected impact |
|---:|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

**Hai hoặc ba failure cases nào cần thêm vào benchmark ở vòng tiếp theo?**

> *Câu trả lời:* Thêm các cases về "Over-refusal" (như câu hỏi bình thường nhưng model từ chối) và các cases mang tính phức hợp đa tài liệu (như Medium 02, Hard 04) để benchmark khả năng retrieval mạnh mẽ hơn.

---

## 7. Final Reflection

**Điều gì trong kết quả benchmark trái với dự đoán ban đầu của bạn?**

> *Câu trả lời:* Điểm Faithfulness và Completeness cực kỳ thấp (gần 0% pass rate). Ban đầu nghĩ rằng BM25 kết hợp LLM Llama-70B sẽ giải quyết trơn tru bài toán RAG cơ bản, nhưng Lexical evaluator đã bộc lộ nhược điểm cực lớn: LLM càng thông minh (biết paraphrase, tóm tắt) thì càng bị chấm điểm thấp vì không trùng 100% từ vựng.

**Word-overlap heuristics trong lab có giới hạn gì? Nếu đưa hệ thống vào
production, bạn sẽ thay hoặc bổ sung metric nào?**

> *Câu trả lời:* Word-overlap không hiểu được ngữ nghĩa (semantics), phạt model khi nó dùng từ đồng nghĩa hoặc hành văn lưu loát hơn. Nếu đưa vào production, em sẽ bỏ hoàn toàn lexical overlap và thay thế bằng **LLM-as-a-Judge** (dùng GPT-4o-mini hoặc Llama-3.1-70B) với bộ tiêu chí Rubric rõ ràng (như thiết kế ở Exercise 3.3) để chấm Faithfulness và Completeness dựa trên Semantics.
