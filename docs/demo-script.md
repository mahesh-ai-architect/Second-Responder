# Second Responder demo script

This version uses shorter sentences and everyday language. Aim for **2:30–2:45**,
including clicks and the live response. The assignment limit is **under 3:00**.
Read only the quoted paragraphs. The screen cues are reminders for you.
Rehearse once with the actual workflow; response time can vary.

## Before recording

- Open GitHub, the three workflow canvases, the imported chat that uses the new
  ingestion namespace, and the completed evaluation workbook.
- Keep the question below ready to paste. You do not need to read the commands
  in the answer aloud.
- Use the synthetic runbooks and keep credential screens out of the recording.
- Say “n-eight-n” for n8n. Say the evaluation scores slowly.
- If the live answer changes a required condition, describe the error rather
  than reading the success paragraph below.

## 0:00–0:20 — Show the GitHub repository

> When an on-call engineer gets an alert, the first question is: what do I do now?
> I built Second Responder to help answer that question. It lets engineers ask
> about an alert in chat and get steps from twelve sample runbooks, with links
> back to the source.

## 0:20–0:45 — Show the three workflow canvases

> I built this using n8n, OpenAI, and Pinecone. There are three workflows.
> The first loads the runbooks and creates embeddings, which let us search by
> meaning. The second finds the three closest matches to a question.
> The third uses that text to write the chat response and add source links.

## 0:45–1:30 — Ask a question in chat

Paste and submit:

```text
What should I check when payments-api /charge returns 5xx errors and Stripe requests time out?
```

While the response loads:

> Here, I’m asking about payment failures and Stripe timeouts.
> The workflow searches the runbooks before asking the model to answer.

When the answer appears, scroll through the checks and conditional actions.
Open one citation if time permits.

> The response shows what to check, what actions apply, and when to escalate.
> Each step links to a runbook so the engineer can verify it.

If the live answer is incorrect, replace that last paragraph with:

> This answer changed a condition from the runbook. I would flag that in my
> evaluation. A source link by itself does not make the advice correct.

## 1:30–2:15 — Show the evaluation workbook

Point to the original payments row and the two prompt-v3 retests.

> I also checked whether the answers stayed faithful to the retrieved text.
> I counted supported claims and tracked critical errors separately.
> One answer scored ninety-four percent but recommended a database runbook
> without requiring confirmation that the connection pool was saturated.
> I revised the prompt to keep each action tied to its original condition.
> Two follow-up answers scored one hundred percent and ninety-two percent,
> with no critical errors identified in those reviews.

## 2:15–2:40 — Show PROJECT.md and the workflow files

> These are early results; more testing is needed before claiming ninety-percent
> faithfulness overall. Real company data would also need controls before going
> to external services.
> The repository includes the workflows, code, runbooks, evaluation results,
> and project report.

## After rehearsal

- Check the actual recording duration. If it runs long, shorten the canvas tour
  and skip opening a citation. Keep the evaluation explanation.
- The live response may take around thirty seconds based on the observed tests;
  leave room for it rather than rushing the narration.
- Review the recording, then add its Loom URL to `PROJECT.md`.
