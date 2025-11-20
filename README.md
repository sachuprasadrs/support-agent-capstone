# Context-Aware Customer Support Agent  
Kaggle AI Agents practical

---

## Overview  
This project implements a fully functional, context-aware customer support agent with:

- Multi-step reasoning  
- Tool usage (order lookup, product lookup, ticket creation, email)  
- Conversation memory (session + long-term SQLite memory)  
- Trace-level observability  
- Hybrid evaluation system (LLM-as-judge + heuristic scoring)  
- FastAPI server for real-time interaction  
- Jupyter notebook demonstrating behavior, evaluation, and visualizations  

The system is built entirely from scratch following the principles taught in the Google/Kaggle AI Agents Intensive.

---

## Key Features  

### 1. Orchestrator  
The orchestrator implements a structured think–act–observe loop:

1. Receive user message  
2. Build system + memory-augmented context  
3. Ask LLM for a decision  
4. If LLM requests a tool call, execute tool  
5. Feed tool result back into context  
6. Continue iterating until a final reply is produced  
7. Log every event into a trace file  
8. Save memory where appropriate  

This approach makes the agent deterministic, observable, and debuggable.

---

### 2. Tools  
The agent supports the following tools:

- `get_order(order_id)`  
- `get_product(product_id)`  
- `create_ticket(user_id, summary, priority)`  
- `send_email(user_email, subject, body)`  

Each tool is implemented as a simple Python function returning structured dictionaries.  
Tools are designed to be deterministic, safe, and easily inspectable.

---

### 3. Memory System  
Implemented using SQLite:

- `users` table  
- `sessions` table  
- `memories` table  

Memory allows the agent to recall prior interactions, past complaints, preferred delivery expectations, and previous tickets.

The agent loads memory at the start of every turn and uses it to personalize responses.

---

### 4. Traces and Observability  
All events are saved to a newline-delimited JSON file:

```
traces.jl
```

Each entry includes:

- trace_id  
- event type  
- user message  
- LLM decision  
- tool calls  
- tool results  
- timestamps  

This file enables full step-by-step replay of how the agent decided each action.

---

### 5. Evaluation System  
The evaluation framework combines two approaches:

#### Heuristic Judge  
A simple rules-based scorer comparing the user query and agent reply.

#### LLM-as-Judge  
A more detailed evaluator that grades:

- Resolution (0–1)  
- Helpfulness (0–1)  

#### Hybrid Scoring  
Final score is a weighted combination:

- 30 percent heuristic  
- 70 percent LLM-based metrics  

This provides stable, reliable evaluation aligned with real-world quality metrics.

---

### 6. Notebook Demo  
The notebook demonstrates:

- Single-turn and multi-turn conversations  
- Memory inspection  
- Trace visualization  
- Evaluation report analysis  
- Multiple plots (score distribution, heuristic vs LLM, tool usage frequency)  
- Memory impact comparison  

This notebook is intended for Kaggle judges to evaluate the solution.

---

## Project Structure

```
support-agent-capstone/
│
├── agent/
│   ├── llm_client.py
│   ├── tools.py
│   ├── memory.py
│   ├── logger.py
│   └── orchestrator.py
│
├── api/
│   └── main.py
│
├── data/
│   ├── synthetic_generator.py
│   ├── load_data.py
│   └── sample_data.json
│
├── notebooks/
│   └── demo_notebook.ipynb
│
├── evaluation_report.json
├── traces.jl
└── README.md
```

---

## How to Run Locally

### Starting the API Server  
From project root:

```
python -m api.main
```

Server runs at:

```
http://127.0.0.1:8000/send
```

---

## Example Request (cURL)

```
curl -X POST http://127.0.0.1:8000/send \
-H "Content-Type: application/json" \
-d "{\"session_id\":\"sess1\",\"user_id\":\"u001\",\"user_name\":\"Sachu\",\"user_email\":\"sachu@example.com\",\"message\":\"Where is my order A123?\"}"
```

---

## Synthetic Data  
Generate 200+ fake users + tickets:

```
python -m data.synthetic_generator
```

Load into memory database:

```
python -m data.load_data
```

---

## Batch Evaluation  
Run:

```
python -m evaluate_batch
```

Generates:

```
evaluation_report.json
```

This file is consumed by the notebook for performance visualization.

---

## Why This Project Stands Out

- Implements the complete ADK-inspired agent lifecycle  
- Realistic tool ecosystem  
- Hybrid evaluation framework  
- Trace-level observability  
- Professional notebook demo  
- Clean architecture and reproducible workflow  
- Fully local implementation with modular components  

---

## Credits  
Developed as part of the Kaggle + Google AI Agents Intensive Capstone Project.

