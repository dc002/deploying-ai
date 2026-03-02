import gradio as gr
import re
from guardrails import violates_guardrails
from services.service1 import get_country_info
from services.service2 import semantic_search, rerank
from services.service3 import simple_math_tool


# -----------------------------
# History helper
# -----------------------------
def log_and_return(user_input: str, system_output: str, history: list):
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": system_output})
    return system_output, history


# -----------------------------
# Intent classification
# -----------------------------
def classify_intent(message: str) -> str:
    text = message.lower().strip()

    # System override attempts
    if any(p in text for p in [
        "ignore system",
        "ignore system prompts",
        "please ignore",
        "ignore all instructions",
        "forget previous instructions",
        "forget all instructions",
    ]):
        return "system_override"
    
    # Math-related
    if re.search(r"\b(add|subtract|multiply|times|divide|even)\b", text):
        return "math"


    # Country-related
    if any(word in text for word in [
        "capital", "population", "country", "border",
        "currency", "about", "state of", "nation of",
        "where is", "in what continent", "in which continent"
    ]):
        return "country"

    # Default: semantic search
    return "semantic"


# -----------------------------
# Math normalization
# -----------------------------
def normalize_math_query(message: str) -> str:
    text = message.lower().strip()

    # even/odd checks
    match_even = re.search(r"(is\s+)?(\d+)\s+even\??", text)
    if match_even:
        return f"even {match_even.group(2)}"

    # add
    match_add = re.search(r"add\s+(\d+)\s+(and\s+)?(\d+)", text)
    if match_add:
        return f"add {match_add.group(1)} {match_add.group(3)}"

    # subtract
    match_sub = re.search(r"subtract\s+(\d+)\s+(from\s+)?(\d+)", text)
    if match_sub:
        # "subtract 3 from 10" → 10 - 3
        return f"subtract {match_sub.group(3)} {match_sub.group(1)}"

    # multiply
    match_mult = re.search(r"multiply\s+(\d+)\s+(and|by)\s+(\d+)", text)
    if match_mult:
        return f"multiply {match_mult.group(1)} {match_mult.group(3)}"

    # divide
    match_div = re.search(r"divide\s+(\d+)\s+by\s+(\d+)", text)
    if match_div:
        return f"divide {match_div.group(1)} {match_div.group(2)}"

    # Fallback: return original
    return text


# -----------------------------
# Country name extraction
# -----------------------------
def extract_country_query(message: str) -> str:
    text = message.strip()
    lower = text.lower()

    # Phrases that often introduce the country
    introducers = ["about ", "of ", "on ", "for ", "regarding "]

    # Leading filler phrases before the actual country name
    leading_fillers = [
        "the country ",
        "country ",
        "the nation ",
        "nation ",
        "the state of ",
        "state of ",
        "the republic of ",
        "republic of ",
    ]

    # Trailing polite words
    trailing_words = ["please", "thanks", "thank you", "thx"]

    candidate = text

    # try to cut at the last introducer
    for intro in introducers:
        if intro in lower:
            idx = lower.rfind(intro)
            candidate = text[idx + len(intro):].strip()
            break

    # remove leading fillers
    for filler in leading_fillers:
        if candidate.lower().startswith(filler):
            candidate = candidate[len(filler):].strip()

    # remove trailing polite words
    for w in trailing_words:
        if candidate.lower().endswith(w):
            candidate = candidate[: -len(w)].strip()

    # strip extra punctuation/spaces
    return candidate.strip(" ,.!?").strip()


# -----------------------------
# Personality wrapper
# -----------------------------
def apply_personality(response: str) -> str:
    return f"{response}\n\nLet me know what else you'd like to explore."


# -----------------------------
# Chatbot core
# -----------------------------
def chatbot(message: str, history: list):
    guard = violates_guardrails(message)
    if guard:
        return log_and_return(message, guard, history)

    intent = classify_intent(message)

    if intent == "math":
        normalized = normalize_math_query(message)
        result = simple_math_tool(normalized)
        if result is None:
            result = "I wasn't sure what math you wanted me to do."

    elif intent == "country":
        country_query = extract_country_query(message)
        result = get_country_info(country_query)

    elif intent == "system_override":
        result = "I can't ignore my system instructions, but I'm here to help with your question."

    else:
        candidates = semantic_search(message, top_k=5)
        result = rerank(message, candidates)


    response = apply_personality(result)
    return log_and_return(message, response, history)


# -----------------------------
# Gradio wrapper
# -----------------------------
def chat_wrapper(message, history):
    bot_reply, updated_history = chatbot(message, history)
    return updated_history, updated_history, ""


# -----------------------------
# UI
# -----------------------------
with gr.Blocks() as demo:
    gr.Markdown("# Multi‑Service Chatbot")

    gr.Markdown(
        """
### How to use this chatbot

You can ask questions in natural language, and the chatbot will figure out what you need.  

- **Country information** — Ask about a country's capital, population, region, or general facts.  
  *Examples:* "Tell me about Japan", "What's the capital of France?", "population of Brazil".

- **Semantic search** — Ask for summaries, themes, or information related to the embedded documents.  
  *Examples:* "plot", "story", "main characters".

- **Simple math** — Perform basic arithmetic or even/odd checks.  
  *Examples:* "add 5 and 12", "subtract 10 from 2", "multiply 7 and 8", "divide 10 by 2", "is 42 even?".

Type your message and press **Enter** or click **Send** to start the conversation.
"""
    )

    session_history = gr.State([])

    chat = gr.Chatbot(label="Conversation", autoscroll=True)

    user_input = gr.Textbox(
        label="Type your message",
        lines=1
    )

    user_input.submit(
        fn=chat_wrapper,
        inputs=[user_input, session_history],
        outputs=[chat, session_history, user_input],
    )

    send_btn = gr.Button("Send")
    send_btn.click(
        fn=chat_wrapper,
        inputs=[user_input, session_history],
        outputs=[chat, session_history, user_input],
    )

    clear_btn = gr.Button("Clear Conversation")
    clear_btn.click(
        fn=lambda: ([], [], ""),
        inputs=None,
        outputs=[chat, session_history, user_input],
    )

if __name__ == "__main__":
    demo.launch()