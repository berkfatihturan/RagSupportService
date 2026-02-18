import requests
import json
import os

BASE_URL = "http://localhost:8000"

def create_dummy_files():
    with open("test_flower.txt", "w") as f:
        f.write("The rose is a woody perennial flowering plant of the genus Rosa, in the family Rosaceae. There are over three hundred species and tens of thousands of cultivars.")
    
    with open("test_car.txt", "w") as f:
        f.write("A car (or automobile) is a wheeled motor vehicle used for transportation. Most definitions of cars say that they run primarily on roads, seat one to eight people, have four wheels, and mainly transport people rather than goods.")

def test_root():
    print("Testing Root Endpoint...")
    try:
        r = requests.get(BASE_URL + "/")
        print(r.json())
        assert r.status_code == 200
    except Exception as e:
        print(f"Failed to connect to {BASE_URL}. Make sure the server is running. Error: {e}")
        return False
    return True

def test_ingest():
    print("\nTesting Ingestion (Async)...")
    import time
    
    # Ingest Flower
    files = {'file': open('test_flower.txt', 'rb')}
    data = {
        'keys': json.dumps(["category:flowers", "source:wiki"]),
        'metadata': json.dumps({"author": "test_bot"})
    }
    r = requests.post(BASE_URL + "/ingest", files=files, data=data)
    print("Ingest Request:", r.json())
    
    if r.status_code == 200:
        job_id = r.json().get("job_id")
        print(f"Tracking Job {job_id}...")
        
        while True:
            r_job = requests.get(f"{BASE_URL}/job/{job_id}")
            job_status = r_job.json().get("status")
            print(f"Job Status: {job_status}")
            
            if job_status in ["COMPLETED", "FAILED", "PARTIAL"]:
                print("Final Job Result:", json.dumps(r_job.json(), indent=2))
                break
            
            time.sleep(1)
    
    # Ingest Car
    files = {'file': open('test_car.txt', 'rb')}
    data = {
        'keys': json.dumps(["category:cars", "tech"]),
        'metadata': json.dumps({"author": "test_bot"})
    }
    # Just fire and forget for car, let's proceed to search test after a small delay
    requests.post(BASE_URL + "/ingest", files=files, data=data)
    time.sleep(2)

def test_search():
    print("\nTesting Search...")
    
    # 1. Search for 'rose' with flower filter (Should match)
    query = {
        "query": "What is a rose?",
        "filter_keys": ["category:flowers"],
        "top_k": 1
    }
    r = requests.post(BASE_URL + "/search", json=query)
    print("Search 'Rose' in Flowers:", json.dumps(r.json(), indent=2))
    
    # 2. Search for 'car' with flower filter (Should NOT match or be low score if vector search ignores filter, but our logic enforces filter)
    # Our simple mock logic in vector_db.py enforces filter.
    query = {
        "query": "Tell me about cars.",
        "filter_keys": ["category:flowers"],
        "top_k": 1
    }
    r = requests.post(BASE_URL + "/search", json=query)
    print("Search 'Cars' in Flowers (Should be empty/irrelevant):", json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    if not os.path.exists("test_flower.txt"):
        create_dummy_files()
        
    print("NOTE: Ensure 'uvicorn src.main:app --reload' is running in another terminal.")
    if test_root():
        test_ingest()
        test_search()
        
    # Cleanup
    if os.path.exists("test_flower.txt"): os.remove("test_flower.txt")
    if os.path.exists("test_car.txt"): os.remove("test_car.txt")
