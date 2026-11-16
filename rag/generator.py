import os
import warnings
from typing import List, Dict, Any, Optional

warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
import config

RAG_SYSTEM_PROMPT = """You are a precise, document-grounded AI assistant.
Your task is to answer the user's question using the provided document context snippets.

Strict Grounding Rules:
1. Answer using the information explicitly stated or outlined in the context snippets below.
2. If the user asks for topics, summaries, or key concepts of the document, synthesize them directly from the provided context.
3. Do NOT invent facts or extrapolate beyond what the context states.
4. If the context has absolutely no relevance or information to answer the question, respond with:
   "I could not find this information in your uploaded documents."
5. Whenever possible, reference the source document name and page number.
6. Keep your answers clear, well-structured, and helpful.
"""

NORMAL_SYSTEM_PROMPT = """You are a helpful, knowledgeable AI assistant.
Answer the user's question directly to the best of your general knowledge.
Do not refer to any external documents since none were provided.
"""

FAST_FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-pro-latest"
]


class AnswerGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self._active_model_name = "gemini-2.5-flash"
        self._available_models: List[str] = []
        if self.api_key:
            self._configure_api(self.api_key)

    def _configure_api(self, api_key: str):
        try:
            cleaned_key = api_key.strip()
            genai.configure(api_key=cleaned_key)
            self.api_key = cleaned_key
            self._active_model_name = "gemini-2.5-flash"
        except Exception as e:
            warnings.warn(f"Failed to configure Gemini API: {str(e)}")

    def set_api_key(self, api_key: str):
        if api_key and api_key.strip():
            self._configure_api(api_key.strip())

    def _discover_models(self):
        try:
            available = []
            for m in genai.list_models():
                methods = getattr(m, "supported_generation_methods", [])
                if "generateContent" in methods:
                    name = m.name.replace("models/", "")
                    available.append(name)
            self._available_models = available

            for pref in FAST_FALLBACK_MODELS:
                if pref in available:
                    self._active_model_name = pref
                    return

            if available:
                self._active_model_name = available[0]
            else:
                self._active_model_name = "gemini-2.5-flash"
        except Exception:
            self._active_model_name = "gemini-2.5-flash"

    def _get_candidate_models(self) -> List[str]:
        candidates = []
        if self._active_model_name:
            candidates.append(self._active_model_name)
        for m in FAST_FALLBACK_MODELS:
            if m not in candidates:
                candidates.append(m)
        return candidates[:4]

    def _generate_with_fallback(self, prompt: str, system_instruction: str) -> str:
        candidates = self._get_candidate_models()
        last_error = None

        for model_name in candidates:
            try:
                active_prompt = prompt
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=system_instruction
                    )
                except (TypeError, ValueError):
                    model = genai.GenerativeModel(model_name=model_name)
                    active_prompt = f"{system_instruction}\n\n{prompt}"

                response = model.generate_content(
                    active_prompt,
                    request_options={"timeout": 15}
                )

                if response and response.text:
                    self._active_model_name = model_name
                    return response.text.strip()
            except Exception as e:
                err_str = str(e)
                last_error = err_str
                if "API_KEY_INVALID" in err_str or "400" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    raise RuntimeError(err_str)
                continue

        raise RuntimeError(last_error or "Unable to generate response from Gemini API.")

    def generate_rag_answer(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not retrieved_chunks:
            return {
                "answer": "I could not find this information in your uploaded documents.",
                "sources": [],
                "success": True,
                "error": None
            }

        if not self.api_key:
            return {
                "answer": "⚠️ Google Gemini API key is missing. Please set your key in `.env` or in the Key Settings.",
                "sources": [],
                "success": False,
                "error": "Missing GEMINI_API_KEY"
            }

        context_blocks = []
        sources = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            src = chunk.get("source", "Unknown")
            page = chunk.get("page", 1)
            score = chunk.get("similarity_score", 0.0)
            text = chunk.get("text", "").strip()

            source_ref = f"{src} (Page {page})"
            if source_ref not in sources:
                sources.append(source_ref)

            context_blocks.append(
                f"[Source: {src} | Page: {page} | Score: {score:.2f}]\n{text}"
            )

        context_text = "\n\n".join(context_blocks)

        prompt = (
            f"=== RETRIEVED DOCUMENT CONTEXT ===\n"
            f"{context_text}\n\n"
            f"=== USER QUESTION ===\n"
            f"{question}\n\n"
            f"=== GROUNDED ANSWER ==="
        )

        try:
            answer_text = self._generate_with_fallback(
                prompt=prompt,
                system_instruction=RAG_SYSTEM_PROMPT
            )
            return {
                "answer": answer_text,
                "sources": sources,
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "answer": f"⚠️ Gemini API Error: {str(e)}",
                "sources": [],
                "success": False,
                "error": str(e)
            }

    def generate_normal_answer(self, question: str) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "answer": "⚠️ Google Gemini API key is missing. Please set your key in `.env` or in the Key Settings.",
                "success": False,
                "error": "Missing GEMINI_API_KEY"
            }

        prompt = f"Question: {question}\n\nAnswer:"

        try:
            answer_text = self._generate_with_fallback(
                prompt=prompt,
                system_instruction=NORMAL_SYSTEM_PROMPT
            )
            return {
                "answer": answer_text,
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "answer": f"⚠️ Gemini API Error: {str(e)}",
                "success": False,
                "error": str(e)
            }
