import re
import math
from typing import List, Dict, Tuple
from collections import Counter

from .config import TOP_K, MIN_SCORE_THRESHOLD, SEMANTIC_WEIGHT, KEYWORD_WEIGHT
from .embeddings import EmbeddingService
from .vector_store import VectorStore

# Türkçe-İngilizce diyabet terimleri sözlüğü (cross-language keyword matching)
_TR_EN_SYNONYMS: Dict[str, List[str]] = {
    "belirti": ["symptom", "symptoms", "sign", "signs", "semptom"],
    "beslenme": ["nutrition", "diet", "dietary", "food", "eating"],
    "egzersiz": ["exercise", "physical", "activity", "workout"],
    "tedavi": ["treatment", "therapy", "management"],
    "insulin": ["insulin"],
    "tani": ["diagnosis", "diagnostic", "screening"],
    "komplikasyon": ["complication", "complications"],
    "hamilelik": ["pregnancy", "pregnant", "gestational", "gebelik"],
    "risk": ["risk", "factor", "factors"],
    "ilac": ["medication", "drug", "pharmacotherapy"],
    "kan": ["blood", "glucose", "glycemic"],
    "seker": ["sugar", "glucose", "glycemic"],
    "ayak": ["foot", "feet", "podiatric"],
    "goz": ["eye", "retinopathy", "vision", "ophthalmic"],
    "bobrek": ["kidney", "renal", "nephropathy"],
    "kalp": ["heart", "cardiac", "cardiovascular"],
    "obezite": ["obesity", "obese", "overweight", "bmi"],
    "stres": ["stress", "anxiety", "psychological", "mental"],
    "agri": ["pain", "neuropathy", "tingling", "numbness"],
    "kilo": ["weight", "loss", "gain", "bmi"],
    "tip": ["type", "type1", "type2"],
    "cocuk": ["children", "pediatric", "child", "school"],
    "yasli": ["elderly", "geriatric", "aging", "older"],
    "oruc": ["fasting", "ramadan"],
    "seyahat": ["travel", "traveling", "trip"],
    "cilt": ["skin", "dermatology", "dermal"],
    "dis": ["dental", "oral", "teeth"],
    "yorgunluk": ["fatigue", "tiredness", "exhaustion"],
    "susuzluk": ["thirst", "polydipsia", "dehydration"],
    "idrar": ["urination", "polyuria", "urine"],
    "bulanik": ["blurred", "vision", "blurry"],
    "yara": ["wound", "healing", "ulcer"],
}


class RAGRetriever:
    """Hybrid RAG retriever: semantic (FAISS) + keyword (BM25-lite) scoring."""

    def __init__(self):
        self._embedding_service = EmbeddingService()
        self._vector_store = VectorStore()
        self._loaded = self._vector_store.load()

        # BM25 parametreleri
        self._k1 = 1.5
        self._b = 0.75
        self._avg_dl = 0.0
        self._doc_freqs: Dict[str, int] = {}
        self._n_docs = 0

        if self._loaded:
            self._build_bm25_stats()
            print(f"RAG retriever ready: {self._vector_store.chunk_count} chunks indexed (hybrid mode).")
        else:
            print("WARNING: No FAISS index found. RAG retrieval will return empty results.")

    def _normalize_turkish(self, text: str) -> str:
        """Türkçe özel karakterleri ASCII'ye dönüştür (BM25 eşleşmesi için)."""
        tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
        return text.translate(tr_map)

    def _tokenize(self, text: str) -> List[str]:
        """Basit Türkçe/İngilizce tokenizer."""
        text = self._normalize_turkish(text.lower())
        tokens = re.findall(r'[a-z0-9]+', text)
        return [t for t in tokens if len(t) > 2]

    def _expand_query_tokens(self, tokens: List[str]) -> List[str]:
        """Türkçe sorgu kelimelerini İngilizce eşdeğerleriyle genişlet."""
        expanded = list(tokens)
        for token in tokens:
            for tr_key, en_values in _TR_EN_SYNONYMS.items():
                # Kök eşleşme: ilk 4 karakter aynıysa eşleştir
                match_len = min(len(token), len(tr_key), 4)
                if match_len >= 3 and token[:match_len] == tr_key[:match_len]:
                    expanded.extend(en_values)
                    break
        return expanded

    def _build_bm25_stats(self):
        """Chunk'lardan BM25 istatistiklerini hesapla."""
        chunks = self._vector_store.chunks
        self._n_docs = len(chunks)
        if self._n_docs == 0:
            return

        total_len = 0
        df: Dict[str, int] = {}

        for chunk in chunks:
            tokens = self._tokenize(chunk["text"])
            total_len += len(tokens)
            seen = set(tokens)
            for token in seen:
                df[token] = df.get(token, 0) + 1

        self._avg_dl = total_len / self._n_docs
        self._doc_freqs = df

    def _bm25_score(self, query_tokens: List[str], doc_text: str) -> float:
        """Tek bir döküman için BM25 skoru hesapla."""
        doc_tokens = self._tokenize(doc_text)
        doc_len = len(doc_tokens)
        if doc_len == 0:
            return 0.0

        tf_map = Counter(doc_tokens)
        score = 0.0

        for qt in query_tokens:
            tf = tf_map.get(qt, 0)
            if tf == 0:
                continue
            df = self._doc_freqs.get(qt, 0)
            idf = math.log((self._n_docs - df + 0.5) / (df + 0.5) + 1.0)
            tf_norm = (tf * (self._k1 + 1)) / (tf + self._k1 * (1 - self._b + self._b * doc_len / max(self._avg_dl, 1)))
            score += idf * tf_norm

        return score

    def _bm25_search(self, query: str, top_k: int) -> List[Tuple[Dict, float]]:
        """Tüm chunk'lar üzerinde BM25 araması yap."""
        query_tokens = self._tokenize(query)
        expanded = self._expand_query_tokens(query_tokens)

        scores = []
        for chunk in self._vector_store.chunks:
            score = self._bm25_score(expanded, chunk["text"])
            if score > 0:
                scores.append((chunk, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    @property
    def chunk_count(self) -> int:
        return self._vector_store.chunk_count

    @property
    def is_ready(self) -> bool:
        return self._loaded and self._vector_store.chunk_count > 0

    def retrieve(self, query: str, top_k: int = TOP_K) -> List[Dict]:
        """
        Hybrid retrieve: FAISS semantic + BM25 keyword (tüm corpus üzerinde).
        İki kaynağı birleştirip RRF (Reciprocal Rank Fusion) ile sıralar.
        """
        if not self.is_ready:
            return []

        # 1) Semantic search (FAISS)
        fetch_k = min(top_k * 6, 60)
        query_embedding = self._embedding_service.embed_query(query)
        semantic_results = self._vector_store.search(query_embedding, fetch_k)

        # 2) BM25 keyword search (tüm corpus, cross-language genişletmeli)
        bm25_results = self._bm25_search(query, fetch_k)

        # 3) RRF (Reciprocal Rank Fusion) ile birleştir
        # Her chunk_id'ye rank-tabanlı skor ver: 1/(k+rank)
        rrf_k = 60  # RRF smoothing constant
        chunk_scores: Dict[int, float] = {}
        chunk_map: Dict[int, Dict] = {}
        chunk_sem_scores: Dict[int, float] = {}

        for rank, (chunk, sem_score) in enumerate(semantic_results):
            cid = chunk["chunk_id"]
            chunk_scores[cid] = chunk_scores.get(cid, 0) + SEMANTIC_WEIGHT / (rrf_k + rank + 1)
            chunk_map[cid] = chunk
            chunk_sem_scores[cid] = sem_score

        for rank, (chunk, bm25_score) in enumerate(bm25_results):
            cid = chunk["chunk_id"]
            base_rrf = KEYWORD_WEIGHT / (rrf_k + rank + 1)
            # BM25-only sonuçlara (semantic'te olmayan) bonus ver
            # Bu, cross-language keyword match'lerin öne çıkmasını sağlar
            if cid not in chunk_sem_scores:
                base_rrf *= 2.5
            chunk_scores[cid] = chunk_scores.get(cid, 0) + base_rrf
            chunk_map[cid] = chunk
            if cid not in chunk_sem_scores:
                chunk_sem_scores[cid] = 0.0

        # 4) Skora göre sırala
        ranked = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)

        # 5) Kaynak çeşitliliği: aynı kaynaktan max 2 chunk
        source_count: dict[str, int] = {}
        retrieved = []
        for cid, rrf_score in ranked:
            chunk = chunk_map[cid]

            src = chunk["source"]
            cnt = source_count.get(src, 0)
            if cnt >= 2:
                continue
            source_count[src] = cnt + 1

            retrieved.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "score": round(rrf_score, 4),
            })
            if len(retrieved) >= top_k:
                break

        return retrieved
