
import sys
import os
import numpy as np

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.app.model import _clean_label

def test_mappings():
    test_cases = [
        ("remote_control", "Smartphone"),
        ("loudspeaker", "Smartphone"),
        ("cellular_telephone", "Apple iPhone"),
        ("hand-held_computer", "Apple iPhone"),
        ("laptop", "Premium Laptop"),
        ("perfume", "Premium Perfume"),
        ("lotion", "Body Lotion"),
        ("sunscreen", "Sunscreen Serum"),
    ]
    
    print("Testing ImageNet Label Mappings:")
    all_passed = True
    for label, expected in test_cases:
        result = _clean_label(label)
        status = "PASS" if result == expected else "FAIL"
        print(f"  {label:25} -> {result:20} | Expected: {expected:20} | {status}")
        if status == "FAIL":
            all_passed = False
            
    if all_passed:
        print("\n✅ All mapping tests passed!")
    else:
        print("\n❌ Some mapping tests failed.")

if __name__ == "__main__":
    test_mappings()
