import itertools
import math

# Function to apply unary operations to a number
def unary_operations(n):
    results = set()
    results.add(n)
    # Apply square root if n is a perfect square
    if n >= 0:
        sqrt_n = math.isqrt(n)
        if sqrt_n * sqrt_n == n:
            results.add(sqrt_n)
    # Apply square and cube if result is reasonable
    for exp in [2, 3]:
        powered = n ** exp
        if powered <= 10000:  # Limit to reasonable size
            results.add(powered)
    return results

# Function to compute all possible results from a list of numbers
def compute(numbers):
    if len(numbers) == 1:
        return numbers
    results = set()
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j:
                rest = [numbers[k] for k in range(len(numbers)) if k != i and k != j]
                num1_set = unary_operations(numbers[i])
                num2_set = unary_operations(numbers[j])
                for num1 in num1_set:
                    for num2 in num2_set:
                        for op in ['+', '-', '*', '/', '**', 'root']:
                            try:
                                if op == '+':
                                    val = num1 + num2
                                elif op == '-':
                                    val = num1 - num2
                                elif op == '*':
                                    val = num1 * num2
                                elif op == '/':
                                    if num2 == 0:
                                        continue
                                    val = num1 / num2
                                elif op == '**':
                                    # Limit exponent to integers to prevent complex numbers
                                    if num2 >= 0 and num2 <= 10 and num1 >= 0:
                                        val = num1 ** num2
                                    else:
                                        continue
                                elif op == 'root':
                                    # Compute num1 root num2
                                    if num2 > 0 and num1 >= 0:
                                        val = num1 ** (1 / num2)
                                        if abs(val - round(val)) < 1e-6:
                                            val = round(val)
                                        else:
                                            continue
                                    else:
                                        continue
                                else:
                                    continue
                                new_numbers = rest + [val]
                                results.update(compute(new_numbers))
                            except:
                                continue
    return results

# Function to generate all possible partitions of the digits into numbers
def partitions(digits):
    n = len(digits)
    result = []
    for i in range(1, 1 << (n - 1)):
        partition = []
        last = 0
        for j in range(n - 1):
            if i & (1 << j):
                num = int(''.join(map(str, digits[last:j+1])))
                partition.append(num)
                last = j + 1
        num = int(''.join(map(str, digits[last:n])))
        partition.append(num)
        result.append(partition)
    # Also include the case where all digits are considered as one number
    result.append([int(''.join(map(str, digits)))])
    return result

# Main function to calculate the percentage
def calculate_percentage():
    successful_numbers = set()
    total_numbers = 10000
    for num in range(10000):
        # Extract digits and replace 0 with 10
        digits = [int(d) if d != '0' else 10 for d in f"{num:04d}"]
        found = False
        # Generate all permutations of the digits
        for perm in set(itertools.permutations(digits)):
            # Generate all possible partitions
            for partition in partitions(perm):
                # Apply unary operations to numbers in the partition
                number_lists = [unary_operations(n) for n in partition]
                # Generate all combinations of numbers after unary operations
                for numbers in itertools.product(*number_lists):
                    # Compute all possible results from these numbers
                    results = compute(list(numbers))
                    if 15 in results or 15.0 in results:
                        successful_numbers.add(num)
                        found = True
                        break
                if found:
                    break
            if found:
                break
    percentage = (len(successful_numbers) / total_numbers) * 100
    print(f"The percentage of numbers that can result in 15 is {percentage:.2f}%")

calculate_percentage()
