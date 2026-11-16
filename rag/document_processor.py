import io
from typing import Dict, Any, List, Union
import fitz


class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_input: Union[str, bytes, io.BytesIO], filename: str = "document.pdf") -> Dict[str, Any]:
        doc = None
        try:
            if isinstance(file_input, str):
                doc = fitz.open(file_input)
            elif isinstance(file_input, bytes):
                doc = fitz.open(stream=file_input, filetype="pdf")
            elif hasattr(file_input, "read"):
                file_bytes = file_input.read()
                if hasattr(file_input, "seek"):
                    file_input.seek(0)
                doc = fitz.open(stream=file_bytes, filetype="pdf")
            else:
                return {
                    "success": False,
                    "filename": filename,
                    "total_pages": 0,
                    "pages": [],
                    "error": f"Unsupported file input type: {type(file_input).__name__}"
                }

            total_pages = len(doc)
            if total_pages == 0:
                return {
                    "success": False,
                    "filename": filename,
                    "total_pages": 0,
                    "pages": [],
                    "error": f"The PDF '{filename}' is empty (0 pages)."
                }

            extracted_pages: List[Dict[str, Any]] = []
            total_characters = 0

            for page_index in range(total_pages):
                page = doc[page_index]
                page_text = page.get_text("text").strip()

                if page_text:
                    total_characters += len(page_text)
                    extracted_pages.append({
                        "page_number": page_index + 1,
                        "text": page_text,
                        "source": filename
                    })
                else:
                    extracted_pages.append({
                        "page_number": page_index + 1,
                        "text": "",
                        "source": filename
                    })

            if total_characters == 0:
                return {
                    "success": False,
                    "filename": filename,
                    "total_pages": total_pages,
                    "pages": [],
                    "error": (
                        f"No readable text found in '{filename}'. "
                        "The document might contain only scanned images without OCR or is encrypted."
                    )
                }

            return {
                "success": True,
                "filename": filename,
                "total_pages": total_pages,
                "pages": extracted_pages,
                "error": None
            }

        except fitz.FileDataError as e:
            return {
                "success": False,
                "filename": filename,
                "total_pages": 0,
                "pages": [],
                "error": f"Corrupt or invalid PDF file '{filename}': {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "filename": filename,
                "total_pages": 0,
                "pages": [],
                "error": f"Failed to process '{filename}': {str(e)}"
            }
        finally:
            if doc is not None:
                doc.close()
