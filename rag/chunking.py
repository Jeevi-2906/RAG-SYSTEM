import re
from typing import List, Dict, Any


class IntelligentChunker:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 120):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_into_sentences(self, text: str) -> List[str]:
        text = re.sub(r'\r\n', '\n', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_page(self, page_text: str, source: str, page_number: int) -> List[Dict[str, Any]]:
        if not page_text or not page_text.strip():
            return []

        sentences = self._split_into_sentences(page_text)
        if not sentences:
            return []

        chunks: List[str] = []
        current_chunk: List[str] = []
        current_len = 0

        for sentence in sentences:
            sent_len = len(sentence)

            if sent_len > self.chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_len = 0

                words = sentence.split()
                temp_chunk: List[str] = []
                temp_len = 0
                for word in words:
                    if temp_len + len(word) + 1 > self.chunk_size and temp_chunk:
                        chunks.append(" ".join(temp_chunk))
                        overlap_words: List[str] = []
                        o_len = 0
                        for w in reversed(temp_chunk):
                            if o_len + len(w) + 1 <= self.chunk_overlap:
                                overlap_words.insert(0, w)
                                o_len += len(w) + 1
                            else:
                                break
                        temp_chunk = overlap_words
                        temp_len = sum(len(w) + 1 for w in temp_chunk)
                    temp_chunk.append(word)
                    temp_len += len(word) + 1

                if temp_chunk:
                    chunks.append(" ".join(temp_chunk))
                continue

            if current_len + sent_len + 1 > self.chunk_size and current_chunk:
                chunk_str = " ".join(current_chunk)
                chunks.append(chunk_str)

                overlap_buffer: List[str] = []
                overlap_len = 0
                for s in reversed(current_chunk):
                    if overlap_len + len(s) + 1 <= self.chunk_overlap:
                        overlap_buffer.insert(0, s)
                        overlap_len += len(s) + 1
                    else:
                        break

                current_chunk = overlap_buffer
                current_len = sum(len(s) + 1 for s in current_chunk)

            current_chunk.append(sentence)
            current_len += sent_len + 1

        if current_chunk:
            final_str = " ".join(current_chunk).strip()
            if not chunks or chunks[-1] != final_str:
                chunks.append(final_str)

        structured_chunks: List[Dict[str, Any]] = []
        clean_source = re.sub(r'[^a-zA-Z0-9_-]', '_', source)

        for idx, chunk_text in enumerate(chunks):
            chunk_id = f"{clean_source}_p{page_number}_c{idx + 1}"
            structured_chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": source,
                    "page": page_number,
                    "chunk_id": chunk_id,
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_text.split())
                }
            })

        return structured_chunks

    def chunk_document(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        source = document_data.get("filename", "unknown.pdf")
        pages = document_data.get("pages", [])
        all_chunks: List[Dict[str, Any]] = []

        for page_info in pages:
            page_num = page_info.get("page_number", 1)
            page_text = page_info.get("text", "")
            page_chunks = self.chunk_page(page_text, source=source, page_number=page_num)
            all_chunks.extend(page_chunks)

        return all_chunks
