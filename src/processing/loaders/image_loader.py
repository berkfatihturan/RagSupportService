from PIL import Image
import pytesseract
import logging

logger = logging.getLogger("rog.loader.image")

def load_image(file_path: str) -> dict:
    """
    Loads an image and attempts to extract text via OCR.
    """
    try:
        image = Image.open(file_path)
        
        # Try OCR
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            logger.warning(f"OCR failed for {file_path}. Tesseract might not be installed. Error: {e}")
            text = ""
            
        return {
            "status": "success",
            "text": text,
            "metadata": {
                "format": image.format,
                "size": image.size,
                "mode": image.mode
            }
        }
    except Exception as e:
        logger.error(f"Error loading image {file_path}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "text": ""
        }
