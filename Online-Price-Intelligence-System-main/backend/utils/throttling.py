import time
import random

def throttle(min_sec=1, max_sec=3):
    """
    Introduces a random delay to prevent rate limiting.
    """
    delay = random.uniform(min_sec, max_sec)
    print(f"Throttling: Waiting {delay:.2f} seconds...")
    time.sleep(delay)
