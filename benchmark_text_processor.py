import time
from text_processor import TextProcessor
import os

os.environ["GOOGLE_API_KEY"] = "test"

start = time.perf_counter()
for _ in range(1000):
    processor = TextProcessor()
end = time.perf_counter()

print(f"Time taken to instantiate TextProcessor 1000 times: {end - start:.4f} seconds")
