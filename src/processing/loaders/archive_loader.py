import zipfile
import os
import logging
import shutil

logger = logging.getLogger("rog.loader.archive")


def load_archive(file_path: str, max_files: int = 50) -> dict:
    """
    Extracts ZIP, reads content of files up to max_files, and concatenates them.
    Returns a single text block.
    """
    processed_count = 0
    combined_text = []
    
    try:
        if not zipfile.is_zipfile(file_path):
             logger.error(f"{file_path} is not a valid zip file")
             return {"status": "error", "error": "Invalid zip", "text": ""}
             
        # Extract to temp folder
        base_name = os.path.basename(file_path)
        extract_folder = os.path.join(os.path.dirname(file_path), base_name + "_extracted")
        
        # Cleanup if exists (fresh start)
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok=True)
            
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
            
        # Import loaders here to avoid circular imports if any, 
        # or better, move logic to ingest but archive_loader is better place for zip logic.
        # We need to reuse the loading logic.
        # Let's simple import.
        from .pdf_loader import load_pdf
        from .text_loader import load_text
        from .image_loader import load_image
        from .office_loader import load_docx, load_xlsx, load_pptx
        
        # Walk and process
        for root, dirs, files in os.walk(extract_folder):
            if processed_count >= max_files:
                combined_text.append(f"\n[WARNING] Max file limit ({max_files}) reached. Stopping processing.")
                break
                
            for file in files:
                if processed_count >= max_files:
                    break
                    
                full_path = os.path.join(root, file)
                filename = file.lower()
                
                # Skip system files
                if filename.startswith(".") or filename.startswith("__macosx"):
                    continue
                
                file_text = ""
                try:
                    if filename.endswith(".pdf"):
                        res = load_pdf(full_path)
                        file_text = res.get("text", "")
                    elif filename.endswith((".docx", ".doc")):
                        res = load_docx(full_path)
                        file_text = res.get("text", "")
                    elif filename.endswith((".xlsx", ".xls")):
                        res = load_xlsx(full_path)
                        file_text = res.get("text", "")
                    elif filename.endswith((".pptx", ".ppt")):
                        res = load_pptx(full_path)
                        file_text = res.get("text", "")
                    elif filename.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
                        res = load_image(full_path)
                        file_text = res.get("text", "")
                    elif filename.endswith((".txt", ".md", ".json", ".csv", ".xml", ".py", ".js")):
                        res = load_text(full_path)
                        file_text = res.get("text", "")
                    else:
                        continue # Skip unsupported
                        
                    if file_text.strip():
                        combined_text.append(f"--- FILE: {file} ---")
                        combined_text.append(file_text)
                        processed_count += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to read file inside zip {file}: {e}")
                    continue

        # Cleanup extracted files to save space? 
        # User might want to keep them? 
        # For now, let's keep them or delete. 
        # Usually temp extraction should be cleaned.
        try:
            shutil.rmtree(extract_folder)
        except:
            pass

        return {
            "status": "success",
            "text": "\n".join(combined_text),
            "metadata": {
                "type": "zip_archive",
                "processed_files_count": processed_count,
                "limit_reached": processed_count >= max_files
            }
        }

    except Exception as e:
        logger.error(f"Error extracting zip {file_path}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "text": ""
        }

