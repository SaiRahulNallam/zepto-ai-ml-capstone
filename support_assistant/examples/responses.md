# API Response Evidence

## Example 1 — Policy Question

### Request

```json
{
  "query": "What are the customer support hours?"
}
```

### Actual Response

```json
{"answer":"Based on the retrieved context: Zepto customer support is available via in-app chat 24 hours a day, 7 days a week, given the time-sensitive nature of quick commerce deliveries. Average in-app chat response time is under 2 minutes. E","sources":["doc_08_chunk_0","doc_06_chunk_0","doc_02_chunk_0"],"confidence":1.0}
```

## Example 2 — General Question

### Request

```json
{
  "query": "Who is the CEO of Zepto?"
}
```

### Actual Response

```json
{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
```