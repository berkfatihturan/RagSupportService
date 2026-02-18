import fitz  # PyMuPDF
import logging

logger = logging.getLogger("rog.loader.pdf")

def load_pdf(file_path: str) -> dict:
    """
    Extracts text from a PDF file.
    Returns a dictionary with text content and metadata (page numbers).
    """
    try:
        doc = fitz.open(file_path)
        full_text = ""
        pages_content = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            # Basic cleanup
            text = text.strip()
            
            if text:
                full_text += text + "\n\n"
                pages_content.append({
                    "page": page_num + 1,
                    "text": text
                })
            else:
                # TODO: If text is empty, it might be an image-only PDF. Trigger OCR.
                logger.warning(f"Page {page_num + 1} in {file_path} seems empty. OCR might be needed.")
        
        doc.close()
        
        return {
            "status": "success",
            "text": full_text,
            "pages": pages_content,
            "needs_ocr": len(full_text.strip()) == 0
        }
        
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "text": "",
            "pages": []
        }
