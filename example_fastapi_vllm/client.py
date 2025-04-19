import requests
import json
import time

def generate_text(prompt, max_tokens=256):
    url = "http://localhost:8000/generate"
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9
    }
    headers = {"Content-Type": "application/json"}
    
    start_time = time.time()
    response = requests.post(url, json=payload, headers=headers)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        print(f"Request completed in {end_time - start_time:.2f} seconds")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    prompt = "Explain quantum computing in simple terms"
    result = generate_text(prompt)
    
    if result:
        print("\n=== Generated Text ===")
        print(result["text"])
        print("\n=== Usage Stats ===")
        print(json.dumps(result["usage"], indent=2))