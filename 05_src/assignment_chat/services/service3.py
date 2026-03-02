def simple_math_tool(message: str) -> str | None:
    text = message.lower()

    try:
        if "add" in text:
            nums = [float(x) for x in text.replace("add", "").split()]
            if len(nums) < 2:
                return "I need at least two numbers to add."
            return f"It looks like the total is {sum(nums)}."

        if "subtract" in text:
            nums = [float(x) for x in text.replace("subtract", "").split()]
            if len(nums) < 2:
                return "I need at least two numbers to subtract."
            return f"Subtract {nums[1]} from {nums[0]}, the difference is {nums[0] - nums[1]}."

        if "multiply" in text or "times" in text:
            cleaned = text.replace("multiply", "").replace("times", "")
            nums = [float(x) for x in cleaned.split()]
            if len(nums) < 2:
                return "I need at least two numbers to multiply."
            product = 1
            for n in nums:
                product *= n
            return f"Multiplying those together gives {product}."

        if "divide" in text:
            nums = [float(x) for x in text.replace("divide", "").split()]
            if len(nums) != 2:
                return "I need at least two numbers to divide."
            if nums[1] == 0:
                return "I can't divide by zero, but you can try another calculation anytime."
            return f"Dividing those gives {nums[0] / nums[1]}."

        if "even" in text:
            nums = text.replace("even", "").split()
            if len(nums) != 1:
                return "I need 1 number to check."
            n = int(nums[0])
            return (
                f"Yes, {n} is even."
                if n % 2 == 0
                else f"No, {n} is odd."
            )

        return None

    except Exception:
        return "I had trouble understanding the numbers you gave me, but you're welcome to try again."