
import json
import os

try:
    content = open('diag_results.json', 'rb').read()
    # Handle UTF-16 from PowerShell or standard UTF-8
    if b'\xff\xfe' in content[:2]:
        text = content.decode('utf-16le', errors='ignore')
    else:
        text = content.decode('utf-8', errors='ignore')
    
    # Remove BOM if present
    if text.startswith('\ufeff'):
        text = text[1:]
        
    data = json.loads(text)
    for item in data:
        print(f"PRICE: {item.get('price')} | TITLE: {item.get('title')}")
except Exception as e:
    print(f"Error: {e}")
