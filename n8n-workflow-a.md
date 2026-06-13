# Workflow A — queue filler

Runs daily in the early morning (e.g. 05:00), before Workflow B sends the email.
Its job: keep the Queue tab topped up so Workflow B always has questions to pick from.

---

## Nodes

### 1. Schedule Trigger
- Trigger: **Cron**
- Expression: `0 5 * * *` (05:00 every day)

---

### 2. Google Sheets — read Queue
- Operation: **Read rows**
- Sheet: `Queue`
- Filter: `status = queued`
- Return: all matching rows

---

### 3. Code — count queued rows
Count the rows returned in step 2.

```js
const queued = $input.all();
return [{ json: { queued_count: queued.length } }];
```

---

### 4. IF — is the queue low?
- Condition: `queued_count < 7`
- **True** → continue to step 5
- **False** → stop (no-op branch, queue is healthy)

---

### 5. Google Sheets — read Domains
- Operation: **Read rows**
- Sheet: `Domains`
- Return: all rows (domain + last_used)

---

### 6. Code — pick least recently used domain
Sort by `last_used` ascending (nulls/blanks sort first). Take the top result.

```js
const rows = $input.all().map(r => r.json);
rows.sort((a, b) => {
  if (!a.last_used) return -1;
  if (!b.last_used) return 1;
  return new Date(a.last_used) - new Date(b.last_used);
});
return [{ json: { chosen_domain: rows[0].domain } }];
```

---

### 7. Google Sheets — read recent questions (avoid-list)
- Operation: **Read rows**
- Sheet: `Queue`
- Return: all rows, sorted by `date_added` descending
- Limit: 15 rows

Then extract just the `question` field in a Code node:

```js
const recent = $input.all().map(r => r.json.question);
return [{ json: { recent_questions: recent } }];
```

---

### 8. HTTP Request — call Claude API
- Method: `POST`
- URL: `https://api.anthropic.com/v1/messages`
- Headers:
  - `x-api-key`: your Anthropic API key (store in n8n credentials)
  - `anthropic-version`: `2023-06-01`
  - `content-type`: `application/json`
- Body (JSON):

```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 256,
  "messages": [
    {
      "role": "user",
      "content": "Generate one daily-learning question for the domain: {{ $json.chosen_domain }}.\n\nThe question must be:\n- About something ordinary a person encounters in normal life\n- Hiding a non-obvious answer beneath it\n- Specific and concrete, not broad\n- Answerable from one decent web page in a single sitting\n- Not already obvious to most adults\n- Spoiler-free — the question must never hint at its own answer\n\nAvoid these recent questions:\n{{ $json.recent_questions.join('\\n') }}\n\nRespond with ONLY valid JSON, no other text:\n{ \"question\": \"...\", \"domain\": \"...\", \"est_minutes\": 15 }"
    }
  ]
}
```

> `est_minutes` should be 15, 30, or 60. Include that instruction in the prompt if you want Claude to decide; otherwise hardcode 15 as the default and adjust manually.

---

### 9. Code — parse Claude response
Extract the JSON from Claude's response content.

```js
const content = $input.first().json.content[0].text;
const parsed = JSON.parse(content);
return [{ json: parsed }];
```

---

### 10. Google Sheets — append row to Queue
- Operation: **Append row**
- Sheet: `Queue`
- Values:
  - `date_added`: `{{ $now.toISODate() }}`
  - `question`: `{{ $json.question }}`
  - `domain`: `{{ $json.domain }}`
  - `est_minutes`: `{{ $json.est_minutes }}`
  - `status`: `queued`
  - `date_sent`: *(leave blank)*

---

### 11. Google Sheets — update Domains tab
- Operation: **Update row**
- Sheet: `Domains`
- Match column: `domain` = `{{ $json.chosen_domain }}`
- Set column: `last_used` = `{{ $now.toISODate() }}`

---

## Flow summary

```
Schedule (05:00)
  → Read Queue (status=queued)
  → Count rows
  → IF count < 7
      → Read Domains
      → Pick least-recently-used domain
      → Read last 15 questions (avoid-list)
      → Call Claude API → parse JSON
      → Append new row to Queue (status=queued)
      → Update Domains last_used
```
