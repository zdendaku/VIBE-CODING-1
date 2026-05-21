import os
import json
import math
from pprint import pprint
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)


# --- Tool implementations ---

def calculate(expression: str):
    """Safely evaluate a math expression."""
    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sqrt": math.sqrt, "pow": pow, "log": math.log,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "pi": math.pi, "e": math.e,
    }
    result = eval(expression, {"__builtins__": {}}, allowed_names)
    return {"expression": expression, "result": result}


def unit_convert(value: float, from_unit: str, to_unit: str):
    """Convert between common units."""
    conversions = {
        ("km", "miles"): 0.621371,
        ("miles", "km"): 1.60934,
        ("kg", "lbs"): 2.20462,
        ("lbs", "kg"): 0.453592,
        ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda v: (v - 32) * 5 / 9,
        ("m", "ft"): 3.28084,
        ("ft", "m"): 0.3048,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key not in conversions:
        return {"error": f"Conversion from {from_unit} to {to_unit} not supported"}
    factor = conversions[key]
    converted = factor(value) if callable(factor) else value * factor
    return {"value": value, "from": from_unit, "to": to_unit, "result": round(converted, 4)}


# --- Tool definitions for the API ---

tools = [
    {
        "name": "calculate",
        "description": "Evaluate a mathematical expression. Supports basic arithmetic (+, -, *, /, **) and functions: sqrt, pow, log, sin, cos, tan, abs, round, min, max. Constants: pi, e.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate, e.g. 'sqrt(144) + 2**3'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "unit_convert",
        "description": "Convert a value between units. Supported: km<->miles, kg<->lbs, celsius<->fahrenheit, m<->ft.",
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "The numeric value to convert"},
                "from_unit": {"type": "string", "description": "Source unit, e.g. 'celsius'"},
                "to_unit": {"type": "string", "description": "Target unit, e.g. 'fahrenheit'"},
            },
            "required": ["value", "from_unit", "to_unit"],
        },
    },
]

available_functions = {
    "calculate": calculate,
    "unit_convert": unit_convert,
}


# --- Agentic loop: process tool calls until LLM is done ---

def run(user_message: str, model="claude-sonnet-4-20250514"):
    print(f"\n{'='*60}")
    print(f"User: {user_message}")
    print(f"{'='*60}\n")

    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system="You are a helpful assistant with access to a calculator and unit converter. Use the tools when you need to compute or convert something.",
            messages=messages,
            tools=tools,
            tool_choice={"type": "auto"},
        )

        # Collect tool calls from the response
        tool_calls = [block for block in response.content if block.type == "tool_use"]

        if not tool_calls:
            # No more tool calls — print final text and return
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"Assistant: {block.text}")
            return response

        # Process each tool call
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tool_call in tool_calls:
            fn = available_functions[tool_call.name]
            result = fn(**tool_call.input)
            print(f"  [tool] {tool_call.name}({tool_call.input}) -> {result}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": json.dumps(result),
            })

        messages.append({"role": "user", "content": tool_results})


# --- Demo ---

if __name__ == "__main__":
    # 1) Calculation
    run("What is the square root of 2025 plus 17 cubed?")

    # 2) Unit conversion
    run("I'm 185 cm tall. How much is that in feet? And convert 72 kg to lbs.")

    # 3) Combined
    run("If a circle has radius 7.5 m, what is its area in square feet?")
