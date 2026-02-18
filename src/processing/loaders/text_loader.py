import logging

logger = logging.getLogger("rog.loader.text")

def load_text(file_path: str) -> dict:
    """
    Loads a text file.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            
        return {
            "status": "success",
            "text": text
        }
    except Exception as e:
        logger.error(f"Error loading text file {file_path}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "text": ""
        }
