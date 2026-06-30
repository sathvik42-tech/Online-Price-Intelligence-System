
import re

def _parse_price(text: str) -> float:
    if not text:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", str(text))
    if cleaned.count('.') > 1:
        parts = cleaned.split('.')
        cleaned = parts[0] + '.' + ''.join(parts[1:])
    try:
        val = float(cleaned) if cleaned else 0.0
        return val
    except ValueError:
        return 0.0

# Test cases
print(f"'Rs. 122' -> {_parse_price('Rs. 122')}")
print(f"122 -> {_parse_price(122)}")
print(f"0.122 -> {_parse_price(0.122)}")
print(f"'0.122' -> {_parse_price('0.122')}")
