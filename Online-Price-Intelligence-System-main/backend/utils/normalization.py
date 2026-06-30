import re

def normalize_name(name):
    """
    Cleans a product name for better comparison.
    - Converts to lowercase.
    - Removes punctuation and special characters.
    - Removes common descriptors (e.g., 'brand new', 'in stock').
    - Removes extra spaces.
    """
    if not name:
        return ""
    
    # 1. Convert to lowercase
    name = name.lower()
    
    # 2. Remove common unnecessary words/phrases
    removable_phrases = [
        r'\bbrand new\b', r'\bin stock\b', r'\bwith warranty\b',
        r'\bfree shipping\b', r'\blowest price\b', r'\bbest deal\b'
    ]
    for phrase in removable_phrases:
        name = re.sub(phrase, '', name)

    # 3. Remove special characters using Regex
    name = re.sub(r'[^a-z0-9\s]', ' ', name)
    
    # 4. Remove extra spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def fuzzy_match(name1, name2, threshold=0.7):
    """
    A simple fuzzy match based on word overlap.
    """
    n1 = set(normalize_name(name1).split())
    n2 = set(normalize_name(name2).split())
    
    if not n1 or not n2:
        return 0.0
        
    intersection = n1.intersection(n2)
    union = n1.union(n2)
    
    return len(intersection) / len(union)

if __name__ == "__main__":
    # Sample test cases to verify the function
    test_names = [
        "  HP Laptop - 14 inch!! ",
        "Apple iPhone 15 Pro (128GB) - Black",
        "Samsung@Galaxy$S24*Ultra   ",
    ]
    
    print("Normalizing product names:\n")
    for original in test_names:
        cleaned = normalize_name(original)
        print(f"Original: '{original}'")
        print(f"Cleaned:  '{cleaned}'\n")
