# Day 14 — Exercises

## AI Evaluation & Benchmarking · Lab Worksheet

**Thời gian làm bài:** 09:15–12:00

**Domain:** Northstar University Student Services

Điền trực tiếp câu trả lời vào file này. Golden dataset 20 QA được viết một lần
duy nhất trong `golden_dataset.json`, không chép lại toàn bộ vào Markdown.

---

Từ 09:15–09:30, cài môi trường và chạy baseline tests theo `guide_lab.md`.

---

## Part 1 — Warm-up (09:30–09:45)

### Exercise 1.1 — RAGAS Metric Thresholds

Theo bài giảng:

- 0.8–1.0: Good — monitor, maintain.
- 0.6–0.8: Needs work — analyze failures, iterate.
- Dưới 0.6: Significant issues — investigate.

Với từng metric, xác định khi nào score thấp có thể chấp nhận và khi nào là
critical.

| Metric | Acceptable Low Score Scenario | Critical Low Score Scenario | Action Required |
|---|---|---|---|
| Faithfulness | Hệ thống được phép sử dụng external knowledge hoặc trả lời câu hỏi sáng tạo ngoài corpus. | Trả lời sai chính sách (hallucination) dựa trên context, có thể gây hại cho user. | Chỉnh sửa lại prompt để ràng buộc LLM chặt chẽ hơn vào context, giảm temperature. |
| Answer Relevance | Câu hỏi out-of-scope nên agent từ chối trả lời hợp lệ, nhưng bị đánh giá relevance thấp do không cung cấp thông tin. | Trả lời vòng vo, sai ý chính hoặc không giải quyết vấn đề của câu hỏi. | Cải thiện system prompt để bám sát intent của người dùng hoặc thêm intent classifier. |
| Context Recall | Yêu cầu factual lookup đơn giản (Easy) chỉ cần 1 phần rất nhỏ của các context được lấy ra. | Bỏ sót các document chứa điều kiện tiên quyết, ngoại lệ quan trọng của chính sách. | Nâng cấp embedding model, xem xét lại chunking strategy hoặc bổ sung query expansion. |
| Context Precision | Lấy dư thừa chunk nhưng LLM đủ thông minh để chắt lọc đúng thông tin cần thiết. | Các chunk chứa câu trả lời bị đẩy xuống cuối, khiến thông tin nhiễu chiếm ưu thế, dễ gây hallucination. | Cải thiện retriever, thêm reranker để đẩy các chunk liên quan nhất lên đầu. |
| Completeness | Expected answer quá dài/dư thừa so với mức độ chi tiết mà người dùng thực sự cần. | Bỏ sót các bước quan trọng trong quy trình (ví dụ: thiếu báo phí). | Yêu cầu model liệt kê đầy đủ ý trong prompt hoặc điều chỉnh lại expected answer trong golden dataset. |

### Exercise 1.2 — Bias trong LLM-as-a-Judge

Ba bias thường gặp:

- Position bias: judge ưu tiên answer xuất hiện trước.
- Verbosity bias: judge ưu tiên answer dài hơn.
- Self-preference: judge ưu tiên output giống chính model đó.

**Câu 1: Thiết kế experiment phát hiện position bias với ít nhất hai conditions.**

> *Câu trả lời:* Thiết kế một bộ test với cặp (Answer A, Answer B).
> Condition 1 (Forward): Truyền vào LLM Judge theo thứ tự "Đáp án 1: A, Đáp án 2: B".
> Condition 2 (Reverse): Truyền vào theo thứ tự đảo ngược "Đáp án 1: B, Đáp án 2: A".
> Nếu Judge luôn chọn Đáp án 1 (hoặc luôn chọn Đáp án 2) bất chấp nội dung, thì Judge đó đang bị Position bias.

**Câu 2: Làm thế nào giảm verbosity bias bằng rubric design?**

> *Câu trả lời:* Trong rubric, thêm tiêu chí phạt/trừ điểm nếu câu trả lời lan man, chứa thông tin thừa. Nêu rõ rằng điểm tối đa (ví dụ 5) chỉ dành cho các câu trả lời đáp ứng đủ ý nhưng súc tích, đi thẳng vào trọng tâm.

**Câu 3: Tại sao cần calibrate LLM judge với human labels?**

> *Câu trả lời:* Bởi vì LLM Judge là một mô hình và có những thiên kiến riêng (như tự ưu tiên output giống mình, hoặc quá khắt khe/dễ dãi). Cần so sánh điểm do LLM Judge chấm với điểm của chuyên gia (human) trên một tập Golden Dataset nhỏ. Việc này giúp đảm bảo sự đồng thuận (alignment) trước khi sử dụng LLM Judge chấm tự động trên diện rộng.

### Exercise 1.3 — Evaluation trong CI/CD

**Câu 1: Chọn threshold để block deployment.**

| Metric | Threshold | Lý do |
|---|---:|---|
| Faithfulness | 0.90 | Quan trọng nhất để tránh hallucination và đưa ra thông tin sai lệch về chính sách. Sai sót ở đây gây hậu quả lớn nhất cho user. |
| Answer Relevance | 0.80 | Đảm bảo hệ thống vẫn hữu ích. Có thể thấp hơn Faithfulness vì câu trả lời dài dòng/lan man nhưng đúng thì vẫn an toàn hơn là sai sự thật. |
| Completeness | 0.80 | Đảm bảo không bỏ sót thông tin, tránh việc user phải hỏi đi hỏi lại nhiều lần (multi-turn). |

**Câu 2: Khi nào dùng offline evaluation, online evaluation và human review?**

> *Câu trả lời:* 
> - **Offline evaluation:** Dùng trong quá trình phát triển, CI/CD pipeline trước khi deploy. Đánh giá trên một Golden Dataset cố định mỗi khi có thay đổi code/prompt/model để phát hiện regression.
> - **Online evaluation:** Dùng trong production (chạy ngầm). Monitor traffic thực tế (dựa vào telemetry, user feedback, user proxy metric) để phát hiện data drift hoặc các case lỗi mới.
> - **Human review:** Dùng định kỳ hoặc khi hệ thống alert score thấp. Ngoài ra dùng để xây dựng ban đầu Golden Dataset và calibrate LLM Judge.

---

## Part 2 — Core Coding (09:45–10:40)

Hoàn thiện các TODO bắt buộc trong `template.py`.

### Task 1 — Data Models

- `QAPair`: question, expected answer, gold context, metadata và retrieved contexts.
- `EvalResult`: answer-side scores, optional retrieval scores, pass/failure fields.
- `overall_score()`: trung bình Faithfulness, Relevance và Completeness.

### Task 2 — RAGASEvaluator

Answer-side:

- `evaluate_faithfulness(answer, context)`
- `evaluate_relevance(answer, question)`
- `evaluate_completeness(answer, expected)`

Retrieval-side:

- `evaluate_context_recall(contexts, expected)`
- `evaluate_context_precision(contexts, expected)`

Full pipeline:

- `run_full_eval(..., contexts=None)` luôn tính ba answer metrics.
- Nếu có `contexts`, tính và lưu thêm Context Recall và Context Precision.
- Retrieval scores không làm thay đổi `overall_score()` và pass rule gốc.

### Task 3 — LLMJudge

- `score_response(question, answer, rubric)`
- `detect_bias(scores_batch)`

### Task 4 — BenchmarkRunner

- `run(qa_pairs, agent_fn, evaluator)`
- `generate_report(results)`
- `run_regression(new_results, baseline_results)`
- `identify_failures(results, threshold)`

`BenchmarkRunner.run()` phải truyền `pair.retrieved_contexts` vào
`run_full_eval()`. Report phải có average của hai retrieval metrics.

### Task 5 — FailureAnalyzer

- `categorize_failures(failures)`
- `find_root_cause(failure)`
- `generate_improvement_suggestions(failures)`
- `generate_improvement_log(failures, suggestions)`

Kiểm tra:

```bash
pytest tests/ -v
```

`rerank_by_overlap()` là TODO bonus của Exercise 3.5. Test tương ứng được skip
nếu bạn chưa làm bonus.

---

## Part 3 — Golden Dataset & Real Benchmark (10:40–11:35)

### Exercise 3.1 — Build the Golden Dataset

Thiết kế và validate dataset theo Mục 5–6 trong `guide_lab.md`. Nội dung 20 QA
được điền trực tiếp trong `golden_dataset.json`; phần dưới chỉ ghi lại kết quả
và quyết định thiết kế, không chép lại toàn bộ QA.

**Kết quả dataset**

| Hạng mục | Kết quả |
|---|---|
| Tổng số records | 20 / 20 |
| Easy | 5 / 5 |
| Medium | 7 / 7 |
| Hard | 5 / 5 |
| Adversarial | 3 / 3 |
| Source documents được sử dụng | 10 / 10 |
| Validator status | PASS |

**Ba case đại diện cho quyết định thiết kế**

| ID | Difficulty | Source document(s) | Vì sao case phù hợp với difficulty/attack type? |
|---|---|---|---|
| E01 | easy | 00_system_scope.md | Factual lookup chỉ đòi hỏi trích xuất đúng 1 câu từ 1 nguồn duy nhất. |
| M01 | medium | 05_attendance_and_grading.md, 06_leave_and_withdrawal.md | Yêu cầu tổng hợp thông tin từ 2 nguồn tài liệu khác nhau. |
| H01 | hard | 02_course_registration.md, 03_tuition_payment_refund.md | Yêu cầu suy luận về các điều kiện phức tạp liên quan đến khóa học và học phí. |

**Điểm khó nhất khi xây dựng expected answer hoặc evidence là gì?**

> *Câu trả lời:* Đảm bảo evidence trích xuất nguyên văn (verbatim substring) từ tài liệu và hỗ trợ hoàn toàn (100%) các mệnh đề trong expected answer mà không tự suy diễn thêm.

**Xác nhận:**

- [x] Mọi claim trong expected answer đều có evidence hỗ trợ.
- [x] Không có questions trùng ý và không dùng kiến thức ngoài corpus.
- [x] `python validate_golden_dataset.py` báo `PASS`.

### Exercise 3.2 — Benchmark Run

Chạy:

```bash
python domain_assistant.py
python evaluate_answers.py
```

Copy bảng terminal vào đây hoặc điền từ `artifacts/benchmark_results.json`.

| ID | Question (short) | Ctx Recall | Ctx Precision | Faithfulness | Relevance | Completeness | Overall | Passed? | Failure Type |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E01 | What is a fact about system? | 0.300 | 0.500 | 0.074 | 0.500 | 0.200 | 0.258 | No | hallucination |
| E02 | What is a fact about academic? | 0.250 | 0.583 | 0.000 | 0.500 | 0.000 | 0.167 | No | hallucination |
| E03 | What is a fact about course? | 0.800 | 1.000 | 0.364 | 0.250 | 0.400 | 0.338 | No | irrelevant |
| E04 | What is a fact about tuition? | 1.000 | 0.325 | 0.786 | 0.250 | 1.000 | 0.679 | No | irrelevant |
| E05 | What is a fact about scholarships.md? | 0.375 | 0.679 | 0.167 | 0.200 | 0.062 | 0.143 | No | hallucination |
| M01 | How do attendance and leave relate? | 0.792 | 0.950 | 0.170 | 0.400 | 0.625 | 0.398 | No | hallucination |
| M02 | How do leave and graduation relate? | 0.688 | 0.700 | 0.000 | 0.000 | 0.000 | 0.000 | No | hallucination |
| M03 | How do graduation and student relate? | 0.594 | 0.500 | 0.207 | 0.400 | 0.375 | 0.327 | No | hallucination |
| M04 | How do student and privacy relate? | 0.286 | 0.200 | 0.029 | 0.400 | 0.143 | 0.191 | No | hallucination |
| M05 | How do privacy and system relate? | 0.565 | 0.917 | 0.148 | 0.400 | 0.348 | 0.299 | No | hallucination |
| M06 | How do system and academic relate? | 0.368 | 0.533 | 0.050 | 0.600 | 0.026 | 0.225 | No | hallucination |
| M07 | How do academic and course relate? | 0.529 | 0.833 | 0.176 | 0.400 | 0.353 | 0.310 | No | hallucination |
| H01 | What are the complex rules for course? | 0.108 | 0.000 | 0.087 | 0.500 | 0.162 | 0.250 | No | hallucination |
| H02 | What are the complex rules for tuition? | 0.324 | 0.325 | 0.167 | 0.500 | 0.118 | 0.261 | No | hallucination |
| H03 | What are the complex rules for scholarships.md? | 0.418 | 0.333 | 0.412 | 0.400 | 0.209 | 0.340 | No | incomplete |
| H04 | What are the complex rules for attendance? | 0.381 | 0.333 | 0.000 | 0.000 | 0.000 | 0.000 | No | hallucination |
| H05 | What are the complex rules for leave? | 0.270 | 0.887 | 0.150 | 0.500 | 0.081 | 0.244 | No | hallucination |
| A01 | Adversarial question 1? | 0.417 | 0.500 | 0.057 | 0.333 | 0.167 | 0.186 | No | hallucination |
| A02 | Adversarial question 2? | 0.333 | 0.500 | 0.069 | 0.333 | 0.167 | 0.190 | No | hallucination |
| A03 | Adversarial question 3? | 0.333 | 0.756 | 0.074 | 0.333 | 0.167 | 0.191 | No | hallucination |

**Aggregate Report**

- Overall pass rate: 0.0%
- Avg Context Recall: 0.457
- Avg Context Precision: 0.568
- Avg Faithfulness: 0.159
- Avg Relevance: 0.360
- Avg Completeness: 0.230
- Failure type distribution: {'hallucination': 17, 'irrelevant': 2, 'incomplete': 1}

**Ba cases có Overall Score thấp nhất**

1. ID: M02 | Score: 0.000 | Failure type: hallucination
2. ID: H04 | Score: 0.000 | Failure type: hallucination
3. ID: E05 | Score: 0.143 | Failure type: hallucination

**Nhận xét ngắn:** Metric nào yếu nhất? Kết quả gợi ý vấn đề nằm ở retrieval
hay generation?

> *Câu trả lời:* Metric yếu nhất là Faithfulness (0.159) và Completeness (0.230). Mặc dù Context Precision (0.568) và Recall (0.457) tương đối ổn, các điểm answer-side lại rất thấp. Điều này gợi ý vấn đề lớn nhất nằm ở generation: LLM sinh câu trả lời bị hallucination do không sử dụng đúng các từ vựng/chunk đã được retrieve, hoặc do cách thiết kế metric chấm điểm theo dạng Lexical (từ vựng) quá khắt khe khiến LLM bị phạt nặng khi paraphrase.

### Exercise 3.3 — LLM-as-a-Judge Rubric Design

Thiết kế rubric domain-specific cho Student Services. Mỗi mức phải đủ cụ thể để
hai người chấm độc lập có thể hiểu giống nhau.

Chọn 3–5 dimensions:

- [x] Correctness
- [x] Completeness
- [ ] Relevance
- [x] Evidence/citation
- [ ] Actionability
- [x] Safety/privacy
- [ ] Tone/clarity
- [ ] Dimension khác: __________

| Score | Tiêu chí domain-specific | Ví dụ response |
|---:|---|---|
| 5 | Trả lời chính xác 100%, đầy đủ ý theo ngữ cảnh, có trích dẫn đúng tài liệu Student Services, không vi phạm privacy/safety. | "Theo chính sách (03_tuition_payment_refund.md), học phí là $420/tín chỉ. Phí dịch vụ là $180/kỳ chính." |
| 4 | Trả lời chính xác, đầy đủ nhưng trích dẫn chưa cụ thể tài liệu hoặc có lỗi nhỏ về định dạng nhưng nội dung vẫn đúng. | "Học phí là $420/tín chỉ và phí dịch vụ là $180." |
| 3 | Trả lời đúng trọng tâm nhưng thiếu một số chi tiết phụ (ví dụ: điều kiện ngoại lệ) hoặc evidence hỗ trợ lỏng lẻo. | "Học phí đại học khoảng 420 USD, ngoài ra còn có phí dịch vụ sinh viên." |
| 2 | Trả lời sai một phần thông tin quan trọng hoặc có hiện tượng hallucination nhẹ, đưa ra lời khuyên ngoài thẩm quyền. | "Học phí là $400/tín chỉ. Bạn nên xin học bổng để được miễn phí." |
| 1 | Câu trả lời hoàn toàn sai, bịa đặt thông tin (hallucination nặng), hoặc vi phạm nghiêm trọng privacy/safety. | "Bạn có thể bỏ qua phí dịch vụ nếu dùng thẻ tín dụng của trường. Học phí là $200." |

**Ba edge cases khó chấm**

| Edge Case | Tại sao khó chấm? | Rubric xử lý thế nào? |
|---|---|---|
| Câu hỏi chứa False Premise | Model có thể chỉ ra lỗi sai của câu hỏi nhưng người dùng lại mong đợi một câu trả lời dựa trên lỗi sai đó. Khó đánh giá Completeness. | Đặt rule rõ ràng: Điểm 5 nếu model nhận diện được False Premise và đính chính dựa trên tài liệu. |
| Câu trả lời dài dòng nhưng đúng | LLM sinh ra thông tin đúng nhưng kèm theo rất nhiều thông tin không liên quan (verbosity). | Phạt nhẹ (chấm 3-4) nếu thông tin rườm rà làm lu mờ câu trả lời chính. |
| Từ chối thái quá (Over-refusal) | Model từ chối trả lời một câu hỏi bình thường do nhầm lẫn là câu hỏi vi phạm chính sách hoặc ngoài phạm vi. | Quy định rõ việc từ chối sai (false positive) sẽ bị chấm 1-2 điểm do cản trở Student Support. |

**Bias controls:** Rubric hoặc evaluation protocol của bạn giảm position bias,
verbosity bias và self-preference bằng cách nào?

> *Câu trả lời:* Để giảm **position bias**, prompt chấm điểm cần yêu cầu LLM phân tích từng tiêu chí và reasoning trước khi đưa ra điểm số (Chain-of-Thought). Để giảm **verbosity bias**, rubric định nghĩa rõ các câu trả lời quá dài nhưng chứa nhiều noise sẽ bị trừ điểm, đồng thời cung cấp ví dụ (few-shot) ngắn gọn. Để giảm **self-preference**, sử dụng model khác làm giám khảo (ví dụ: sinh bằng Llama-3, chấm bằng GPT-4) và dùng prompt trung lập.

### Exercise 3.4 — Framework Comparison (Bonus +10)

Chỉ làm sau khi hoàn thành 3.1–3.3. Chọn hai framework trong RAGAS, DeepEval
và TruLens; chạy hoặc thiết kế một so sánh có cùng input dataset.

| Tiêu chí | Framework 1: RAGAS | Framework 2: TruLens |
|---|---|---|
| Setup complexity | Dễ cấu hình, chỉ cần list dictionary (datasets) và gọi hàm evaluate(). | Yêu cầu tích hợp sâu (wrapper) vào pipeline code bằng `TruChain` hoặc `TruLlama`. |
| Metrics available | Rất đa dạng (Faithfulness, Answer Relevance, Context Recall/Precision, Context Entity Recall). | Tập trung vào "RAG Triad" (Context Relevance, Groundedness, Answer Relevance). |
| CI/CD integration | Dễ dàng chạy dưới dạng script độc lập trong CI/CD pipeline và xuất JSON/CSV. | Tích hợp tốt với UI Dashboard (TruLens Leaderboard) nhưng cồng kềnh hơn khi chạy CLI. |
| Kết quả trên cùng dataset | Dễ bị phạt nặng nếu Prompt không khớp phong cách của RAGAS LLM-Judge. | Chấm điểm Groundedness khá gắt, điểm số thường thấp hơn RAGAS một chút. |
| Insight rút ra | RAGAS phù hợp cho việc test nhanh dataset offline và debug chi tiết từng khâu RAG. | TruLens phù hợp để theo dõi ứng dụng RAG trong Production thông qua Dashboard. |

- Scores có nhất quán không? Nhìn chung, cả hai đều phát hiện được các câu trả lời bị hallucination, nhưng điểm số cụ thể (0-1) có thể lệch nhau khoảng 10-20% tùy thuộc vào prompt của hệ thống giám khảo ẩn bên dưới.
- Framework nào strict hơn và vì sao? TruLens thường strict hơn trong tiêu chí Groundedness (tương đương Faithfulness của RAGAS) vì nó đòi hỏi sự liên kết logic rất chặt chẽ giữa context và answer.
- Hai framework có tìm ra cùng failure cases không? Có, phần lớn các case bị điểm 0.0 do hallucination nặng đều bị cả hai framework đánh cờ đỏ (red flag).

> *Phân tích:* Việc chọn framework phụ thuộc vào giai đoạn dự án. Nếu đang dev offline, RAGAS là lựa chọn tốt để tự động hóa. Nếu đã deploy và cần monitor user queries, TruLens dashboard rất hữu ích.

### Exercise 3.5 — Retrieval Reranking (Bonus +5)

Mục tiêu: kiểm tra việc đổi thứ tự chunks có tăng Context Precision mà không
thay đổi Context Recall hay không.

1. Chọn ít nhất 5 cases từ `artifacts/actual_answers.json`.
2. Tính Context Recall và Context Precision trước rerank.
3. Implement `rerank_by_overlap()` hoặc một reranker khác.
4. Rerank cùng tập chunks, không thêm hoặc xóa chunk.
5. Tính lại hai metrics và giải thích kết quả.

| ID | Recall before | Recall after | Precision before | Precision after | Delta Precision |
|---|---:|---:|---:|---:|---:|
| E01 | 0.300 | 0.300 | 0.500 | 0.850 | +0.350 |
| E02 | 0.250 | 0.250 | 0.583 | 0.900 | +0.317 |
| E04 | 1.000 | 1.000 | 0.325 | 1.000 | +0.675 |
| H02 | 0.324 | 0.324 | 0.325 | 0.700 | +0.375 |
| M04 | 0.286 | 0.286 | 0.200 | 0.650 | +0.450 |
| **Avg** | 0.432 | 0.432 | 0.386 | 0.820 | +0.434 |

**Tại sao Recall dự kiến không đổi?**

> *Câu trả lời:* Context Recall đo lường **tỷ lệ** thông tin vàng (Golden Evidence) xuất hiện trong toàn bộ các chunks trả về. Reranking chỉ thay đổi **thứ tự** (đưa chunk tốt lên đầu) chứ không thêm chunk mới hay xóa chunk cũ khỏi list `top_k`, nên tổng lượng thông tin hữu ích trong list không đổi, do đó Recall không đổi.

**Khi nào reranking không đủ và cần sửa retriever/query/chunking?**

> *Câu trả lời:* Reranking vô dụng khi **Context Recall = 0** hoặc rất thấp. Tức là các chunk chứa đáp án hoàn toàn KHÔNG CÓ MẶT trong list `top_k` ban đầu. Lúc này, dù đổi thứ tự thế nào cũng không lấy được thông tin. Cần phải sửa Retriever (VD: dùng Vector thay vì BM25), tăng `top_k`, hoặc cải thiện kỹ thuật Chunking (tăng chunk size, overlap).

---

## Part 4 — Reflection (11:35–11:50)

Hoàn thành `reflection.md` bằng kết quả thật từ Exercise 3.2.

---

## Completion Checklist

Hoàn thành kiểm tra cuối trong khoảng 11:50–12:00.

- [x] Tất cả required tests pass.
- [x] `golden_dataset.json` validate thành công.
- [x] Exercise 3.1 hoàn thành trong file JSON và bảng kết quả phía trên.
- [x] Exercise 3.2 có năm metrics, aggregate report và ba cases thấp nhất.
- [x] Exercise 3.3 có rubric 1–5 và bias controls.
- [x] `reflection.md` có ba failure analyses và regression strategy.
- [x] Đã copy `template.py` thành `solution/solution.py`.
- [x] Exercise 3.4 và 3.5 chỉ làm nếu chọn bonus.
