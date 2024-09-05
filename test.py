import timeit
import re

def contains_number_any(s):
    return any(char.isdigit() for char in s)

def contains_number_regex(s):
    return bool(re.search(r'\d', s))

# Test strings
test_string = "a" * 1000 + "1"  # Modify as needed

# Time the `any()` approach
time_any = timeit.timeit(lambda: contains_number_any(test_string), number=10000)

# Time the regex approach
time_regex = timeit.timeit(lambda: contains_number_regex(test_string), number=10000)

print(f"Time using `any()`: {time_any}")
print(f"Time using regex: {time_regex}")
