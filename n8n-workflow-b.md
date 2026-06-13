# Workflow B — daily emailer

Runs every morning at 06:30, after Workflow A has had time to top up the queue.
Its job: pick the 3 oldest queued questions, email them, mark them sent.

---

## Nodes

### 1. Schedule Trigger
- Trigger: **Cron**
- Expression: `30 6 * * *` (06:30 every day)

---

### 2. Google Sheets — read Queue
- Operation: **Read rows**
- Sheet: `Queue`
- Filter: `status = queued`
- Return: all matching rows

---

### 3. Code — sort and take first 3
Sort by `date_added` ascending (oldest first), take the top 3.

```js
const rows = $input.all().map(r => r.json);
rows.sort((a, b) => new Date(a.date_added) - new Date(b.date_added));
const top3 = rows.slice(0, 3);
return top3.map(r => ({ json: r }));
```

---

### 4. Code — build email body
Combine the 3 questions into a plain-text email. No answers, no links, no hints.

```js
const questions = $input.all().map(r => r.json);

const lines = questions.map((q, i) => {
  return `${i + 1}. ${q.question}\n   Domain: ${q.domain} · ~${q.est_minutes} min`;
});

const body = `Your 3 questions for today:\n\n${lines.join('\n\n')}`;

return [{ json: { subject: "Your 3 questions for today", body, questions } }];
```

---

### 5. Send Email
- To: your email address
- Subject: `{{ $json.subject }}`
- Body: `{{ $json.body }}`
- Format: **plain text**

Use whichever email node fits your setup (Gmail, SMTP, etc.).

---

### 6. Code — prepare row updates
Extract the row identifiers needed to update each of the 3 rows.

```js
const questions = $input.first().json.questions;
const today = new Date().toISOString().slice(0, 10);
return questions.map(q => ({
  json: {
    question: q.question,   // used to match the row
    status: 'sent',
    date_sent: today
  }
}));
```

---

### 7. Google Sheets — mark rows as sent
Run this node once per item (enable **"Execute Once Per Item"** or use a loop).

- Operation: **Update row**
- Sheet: `Queue`
- Match column: `question` = `{{ $json.question }}`
- Set columns:
  - `status` = `sent`
  - `date_sent` = `{{ $json.date_sent }}`

---

## Flow summary

```
Schedule (06:30)
  → Read Queue (status=queued)
  → Sort by date_added asc, take first 3
  → Build email body (questions only, no answers)
  → Send email
  → For each of the 3 rows: update status=sent, date_sent=today
```

---

## Notes

- **Order of workflows**: Workflow A runs at 05:00, Workflow B at 06:30.
  That gives A 90 minutes to fill any gap before B tries to pull questions.
- **Fewer than 3 queued**: If the queue has 0–2 rows when B runs, the email
  will contain fewer than 3 questions. Add an IF guard before the email node
  if you'd rather skip the send entirely when the queue is empty.
- **Row matching**: Matching on the `question` column assumes questions are unique,
  which they should be. If you ever have a collision, switch to matching on an
  auto-incremented `id` column you add to the sheet.
