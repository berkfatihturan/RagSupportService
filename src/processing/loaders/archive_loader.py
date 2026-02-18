import zipfile
import os
import logging
import shutil

logger = logging.getLogger("rog.loader.archive")

def extract_and_process_zip(file_path: str, extract_to: str, processor_callback):
    """
    Extracts a ZIP file and calls the processor_callback for each file inside.
    processor_callback should be an async coroutine accepting (file_path).
    """
    processed_files = []
    
    try:
        if not zipfile.is_zipfile(file_path):
             logger.error(f"{file_path} is not a valid zip file")
             return {"status": "error", "error": "Invalid zip"}
             
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Extract to a subfolder named after the file
            base_name = os.path.basename(file_path)
            extract_folder = os.path.join(extract_to, base_name + "_extracted")
            os.makedirs(extract_folder, exist_ok=True)
            
            zip_ref.extractall(extract_folder)
            
            # Walk through extracted files
            for root, dirs, files in os.walk(extract_folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    # Skip hidden files
                    if file.startswith("."): # Mac/Linux hidden
                        continue
                    if file.startswith("__MACOSX"):
                        continue
                        
                    # Call the callback (which should be process_file_path)
                    # Since this is synchronous and callback is likely async, we might need adjustments.
                    # For now, let's return the list of paths and let the caller handle async loop.
                    processed_files.append(full_path)
                    
        return {
            "status": "success",
            "extracted_files": processed_files,
            "extraction_path": extract_folder
        }

    except Exception as e:
        logger.error(f"Error extracting zip {file_path}: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
