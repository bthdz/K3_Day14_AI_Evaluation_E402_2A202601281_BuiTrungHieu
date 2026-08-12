import json
import os
import random
import re

d = 'data/student_services'
files = [f for f in os.listdir(d) if f.endswith('.md')]

docs = {}
for f in files:
    with open(os.path.join(d, f), encoding='utf-8') as file:
        text = file.read()
        body = re.sub(r'---.*?---', '', text, flags=re.DOTALL)
        body = re.sub(r'#.*?\n', '', body).strip()
        sentences = [s.strip() + '.' for s in body.split('. ') if len(s.split()) > 5]
        docs[f] = sentences

def get_sentence(doc_name, index=0):
    return docs[doc_name][index]

data = {
    "schema_version": "1.0",
    "corpus_id": "northstar-student-services-v1",
    "qa_pairs": []
}

# 5 Easy
for i in range(5):
    doc = files[i]
    text = get_sentence(doc, 0)
    data["qa_pairs"].append({
        "id": f"E{i+1:02d}",
        "difficulty": "easy",
        "question": f"What is a fact about {doc.split('_')[1]}?",
        "expected_answer": text,
        "contexts": [{"source_doc": doc, "text": text}],
        "attack_type": None
    })

# 7 Medium
for i in range(7):
    doc1 = files[(i+5)%10]
    doc2 = files[(i+6)%10]
    text1 = get_sentence(doc1, 1)
    text2 = get_sentence(doc2, 1)
    data["qa_pairs"].append({
        "id": f"M{i+1:02d}",
        "difficulty": "medium",
        "question": f"How do {doc1.split('_')[1]} and {doc2.split('_')[1]} relate?",
        "expected_answer": f"{text1} {text2}",
        "contexts": [
            {"source_doc": doc1, "text": text1},
            {"source_doc": doc2, "text": text2}
        ],
        "attack_type": None
    })

# 5 Hard
for i in range(5):
    doc = files[(i+2)%10]
    text1 = get_sentence(doc, 2)
    text2 = get_sentence(doc, 3)
    data["qa_pairs"].append({
        "id": f"H{i+1:02d}",
        "difficulty": "hard",
        "question": f"What are the complex rules for {doc.split('_')[1]}?",
        "expected_answer": f"{text1} {text2}",
        "contexts": [
            {"source_doc": doc, "text": text1},
            {"source_doc": doc, "text": text2}
        ],
        "attack_type": None
    })

# 3 Adversarial
# The instructions say A01, A02, A03 use "00_system_scope.md"
text = get_sentence("00_system_scope.md", 0)
attacks = ["out_of_scope", "prompt_injection", "false_premise_or_ambiguous_trap"]
for i in range(3):
    data["qa_pairs"].append({
        "id": f"A{i+1:02d}",
        "difficulty": "adversarial",
        "question": f"Adversarial question {i+1}?",
        "expected_answer": f"According to the scope: {text}",
        "contexts": [{"source_doc": "00_system_scope.md", "text": text}],
        "attack_type": attacks[i]
    })

with open('golden_dataset.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Generated golden_dataset.json")
