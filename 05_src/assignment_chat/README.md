# Multi‑Service Chatbot

Thiis 42 even?s project implements a conversational chatbot that routes user questions to different backend services depending on the intent of the query. The chatbot is built with **Gradio** and uses a **modular service architecture** to keep functionality clean, testable, and easy to extend.

The system supports:

- **Country information lookup**  
- **Semantic search over embedded documents using ChromaDB**  
- **Simple math operations with natural‑language normalization**  
- **Guardrails for unsafe or override attempts**  
- **A Gradio UI framework with Enter‑to‑send chat behavior**

Each capability is implemented as an independent service, and the chatbot automatically determines which one to use based on the user’s message.

## 1. System Overview

The chatbot follows a multi‑stage pipeline:

1. **User enters a message**
2. The **intent classifier** determines whether the message is about:
   - math
   - country information
   - semantic search
   - or a system‑override attempt
3. The message is **routed to the appropriate service**
4. The service returns a result
5. A **personality wrapper** adds a friendly closing sentence
6. The result is displayed in the **Gradio chat interface**

### Architecture

```text
+------------------------------------------------------+
|                     User Interface                   |
|                        (Gradio)                      |
+--------------------------+---------------------------+
                           |
                           v
+------------------------------------------------------+
|                 Chatbot Orchestration                |
|        (intent classification + routing logic)       |
+--------------------------+---------------------------+
                           |
                           v
+------------------------------------------------------+
|                    Backend Services                  |
|           - Country Info (service1)                  |
|           - Semantic Search (service2)               |
|           - Math Engine (service3)                   |
+------------------------------------------------------+
```

### Data Flow

```text
User Input
    |
    v
Intent Classifier  -----------------------------+
    |                                           |
    | math -> Math Service (service3)            |
    | country -> Country Service (service1)      |
    | system override -> Guardrail Response      |
    | semantic -> Semantic Search (service2)     |
    v                                           |
Service Output  <-------------------------------+
    |
    v
Personality Wrapper
    |
    v
Gradio Chatbot UI
```

## 2. Services Provided

### A. Country Information Service (`service1`)

This service extracts a country name from the user’s message and returns:

- capital
- population
- region
- general facts

It supports natural language variations such as:

- "Tell me about Japan"
- "What’s the capital of France?"
- "population of Brazil please"

A small internal dataset provides the country information.

### B. Semantic Search Service (`service2`)

This service performs semantic search over `.txt` documents stored in the `data/` folder.

Included documents:

- `the_blue_cross_short_story.txt`
- `the_blue_cross_plot_summary.txt`
- `the_blue_cross_main_characters.txt`
- `Novartis_hits_acquisition_trail.txt`
- `Russia_WTO_talks.txt`

#### How it works

1. All documents are embedded using **ChromaDB**.
2. When the user asks a semantic question, the system retrieves the **top‑k most similar documents**.
3. The search returns a list of **candidates**, each shaped like:

   ```python
   {"id": filename, "text": document_text}
4. A lightweight reranker selects the best match using:
   - filename hints (e.g., "summary", "plot", "character")
   - fallback to the top embedding result
   - This two‑stage retrieval (vector search + reranking) significantly improves accuracy.

#### Normalization

Before semantic search, user text is normalized:

- lowercasing  
- punctuation removal  
- curly apostrophe normalization  

This ensures consistent matching and routing.

### C. Math Service (`service3`)

The math engine supports:

- addition
- subtraction (two‑number)
- multiplication (two‑number)
- division
- even/odd checks

#### Keyword support

- "multiply", "times"
- "subtract", "minus"

#### Natural‑language normalization

The system converts inputs like:

- "subtract 3 from 10" -> `subtract 10 3`
- "multiply 7 and 8" -> `multiply 7 8`
- "is 42 even?" -> `even 42`

This ensures the math engine receives clean, predictable input.

## 3. Intent Classification

The intent classifier uses rule‑based logic:

- **Math** -> if message contains math keywords
- **Country** -> if message contains country‑related keywords
- **System override** -> if user attempts to bypass instructions
- **Semantic search** -> default fallback

Normalization ensures punctuation and capitalization do not affect classification.

## 4. Key Implementation Details

### A. ChromaDB for Semantic Search

Chosen because it is:

- lightweight
- easy to embed documents
- persistent
- supports top‑k retrieval

Ideal for small‑scale semantic search.

### B. Reranking Layer

Embedding‑only search often confuses:

- summary vs. plot
- plot vs. characters

The reranker fixes this by:

- checking for keywords in filenames
- selecting the most appropriate document
- falling back to the top embedding result

### C. Text Normalization

All user input is normalized to improve:

- intent classification
- math parsing
- semantic search routing

### D. Personality Wrapper

All responses end with:

> "Let me know what else you'd like to explore."

### E. Guardrails

The system blocks unsafe or override attempts and returns a safe message instead.

## 5. User Interface (Gradio)

The UI includes:

- a chat window
- a single‑line textbox
- Enter‑to‑send behavior
- a Send button
- a Clear Conversation button

### Enter‑to‑Send

Because the textbox uses `lines=1`, pressing **Enter** submits the message.
This matches typical chat application behavior.

## 6. Running the Application

1. Install dependencies
2. Ensure the `data/` folder contains the `.txt` documents
3. Run:

```bash
    python main.py
```
4. Access the chatbot in your browser at:

```bash
    http://127.0.0.1:7860/


