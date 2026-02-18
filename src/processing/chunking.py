from typing import List

def recursive_character_chunking(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Splits text into chunks of approximately chunk_size characters, 
    respecting sentence boundaries where possible.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        
        # If we are not at the end of the text, try to find a natural break point
        if end < text_len:
            # Look for the last period or newline within the window
            # to avoid cutting words/sentences in half arbitrarily
            lookback_window = text[start:end]
            last_break = max(
                lookback_window.rfind('. '), 
                lookback_window.rfind('\n')
            )
            
            if last_break != -1:
                end = start + last_break + 1 # Include the punctuation/newline
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        start = end - overlap
        if start < 0: # Should not happen unless chunk_size < overlap
             start = 0
             
    return chunks
