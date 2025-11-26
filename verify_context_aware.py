import requests
import json

url = "http://localhost:8000/research"
query = "最近美光可以買嗎 我看記憶體硬碟會不會只是短期的需求瓶頸"
payload = {"query": query}

try:
    print(f"Sending query: {query}")
    response = requests.post(url, json=payload, timeout=120)
    if response.status_code == 200:
        result = response.json()
        print("\n=== FINAL REPORT ===\n")
        print(result.get("final_report"))
        print("\n=== RISK ASSESSMENT ===\n")
        print(result.get("risk_assessment"))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection Error: {str(e)}")
