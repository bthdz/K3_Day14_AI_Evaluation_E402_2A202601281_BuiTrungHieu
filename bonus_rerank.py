def rerank_by_overlap(question: str, chunks: list[dict]) -> list[dict]:
    """
    Rerank chunks based on lexical overlap with the question.
    """
    question_words = set(question.lower().split())
    
    def score_chunk(chunk):
        chunk_words = set(chunk["text"].lower().split())
        return len(question_words.intersection(chunk_words))
    
    return sorted(chunks, key=score_chunk, reverse=True)

if __name__ == "__main__":
    print("Bonus Exercise 3.5: rerank_by_overlap implemented.")
