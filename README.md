"Summarization + Refinement"
## How to run (local)
1. Create virtualenv & install:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
3. Open http://127.0.0.1:8000/docs for the interactive API docs.

## Example usage

1. **Create the Summarization graph**

POST `/graph/create` with JSON:
```json
{
  "nodes": {
    "split_text": "split_text",
    "generate_summaries": "generate_summaries",
    "merge_summaries": "merge_summaries",
    "refine_summary": "refine_summary",
    "check_length": "check_length"
  },
  "edges": {
    "split_text": "generate_summaries",
    "generate_summaries": "merge_summaries",
    "merge_summaries": "refine_summary",
    "refine_summary": "check_length",
    "check_length": null
  },
  "branches": {
    "check_length": {
      "too_long": "refine_summary",
      "ok": null
    }
  }
}
```

2. **Run the graph**

POST `/graph/run` with JSON:
```json
{
  "graph_id": "<graph_id_from_create>",
  "initial_state": {
    "text": "Long text to summarise ...",
    "chunk_size": 1000,
    "limit": 500,
    "summary_sentences_per_chunk": 2
  },
  "run_async": true
}
```

3. Poll `/graph/state/{run_id}` or open websocket to stream logs.

