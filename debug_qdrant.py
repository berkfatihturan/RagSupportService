from qdrant_client import QdrantClient
import sys

try:
    print(f"--- Debugging Qdrant Client ---")
    client = QdrantClient(path="data/qdrant_db_debug")
    print(f"Client type: {type(client)}")
    
    attributes = dir(client)
    print(f"Attributes: {attributes}")
    
    if 'search' in attributes:
        print("SUCCESS: 'search' method found.")
    else:
        print("FAILURE: 'search' method NOT found.")
        # Check for alternatives
        if 'query_points' in attributes:
            print("ALTERNATIVE: 'query_points' found.")
        if 'query' in attributes:
            print("ALTERNATIVE: 'query' found.")

except Exception as e:
    print(f"Error: {e}")
