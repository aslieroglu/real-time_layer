import concurrent.futures
import time

def test_fn(x):
    print("Here", x)
    time.sleep(1)
    
    return f"Processed {x}"

if __name__ == "__main__":
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(test_fn, range(10))

    print(list(results))  # Should print processed outputs
