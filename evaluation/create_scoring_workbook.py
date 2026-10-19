from pathlib import Path
from datetime import datetime, timezone
import hashlib
import re
import xlsxwriter


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'evaluation' / 'Second-Responder-Faithfulness-Scoring.xlsx'
RUN_LIMIT = 200
CLAIM_LIMIT = 2000
CASE_LIMIT = 200
book = xlsxwriter.Workbook(DEST)
book.set_properties({'title': 'Second Responder — Faithfulness Scoring',
                     'subject': 'Manual claim-level RAG evaluation',
                     'author': 'Second Responder',
                     'comments': 'Starter tests; no actual chatbot results are pre-scored.'})
book.set_calc_mode('auto')

navy, teal, blue, pale, gray = '#16324F', '#087F8C', '#1565C0', '#EAF3FB', '#63758A'
fmt = {
    'title': book.add_format({'bold': True, 'font_size': 22, 'font_color': navy}),
    'subtitle': book.add_format({'font_size': 11, 'font_color': gray, 'text_wrap': True, 'valign': 'top'}),
    'head': book.add_format({'bold': True, 'font_color': 'white', 'bg_color': navy, 'text_wrap': True, 'valign': 'vcenter'}),
    'section': book.add_format({'bold': True, 'font_size': 13, 'font_color': teal}),
    'input': book.add_format({'font_color': blue, 'text_wrap': True, 'valign': 'top'}),
    'input_pct': book.add_format({'font_color': blue, 'num_format': '0%', 'bg_color': pale}),
    'body': book.add_format({'text_wrap': True, 'valign': 'top'}),
    'formula': book.add_format({'bg_color': '#F3F5F7', 'text_wrap': True, 'valign': 'top'}),
    'percent': book.add_format({'num_format': '0.0%', 'bg_color': '#F3F5F7', 'valign': 'top'}),
    'big': book.add_format({'bold': True, 'font_size': 19, 'font_color': navy, 'bg_color': pale}),
    'big_pct': book.add_format({'bold': True, 'font_size': 19, 'font_color': navy, 'num_format': '0.0%', 'bg_color': pale}),
    'link': book.add_format({'font_color': blue, 'underline': True, 'text_wrap': True, 'valign': 'top'}),
    'good': book.add_format({'font_color': '#176B3A', 'bg_color': '#E5F4E9'}),
    'bad': book.add_format({'font_color': '#A12622', 'bg_color': '#FDE9E7'}),
    'warn': book.add_format({'font_color': '#8A5A00', 'bg_color': '#FFF3D6'}),
}

guide = book.add_worksheet('Start Here')
dash = book.add_worksheet('Dashboard')
cases = book.add_worksheet('Test Cases')
runs = book.add_worksheet('Responses')
claims = book.add_worksheet('Claim Review')
refs = book.add_worksheet('Runbook Reference')
example = book.add_worksheet('Worked Example')

for sheet in book.worksheets():
    sheet.hide_gridlines(2)
    sheet.set_tab_color(teal)
    sheet.set_landscape()
    sheet.set_paper(9)
    sheet.fit_to_pages(1, 0)

def banner(sheet, title, subtitle, last_col):
    sheet.merge_range(0, 0, 0, last_col, title, fmt['title'])
    sheet.set_row(0, 33)
    sheet.merge_range(1, 0, 2, last_col, subtitle, fmt['subtitle'])
    sheet.set_row(1, 22)
    sheet.set_row(2, 22)

def table(sheet, name, headers, count):
    sheet.add_table(4, 0, 4 + count, len(headers) - 1, {
        'name': name, 'style': 'Table Style Medium 2',
        'columns': [{'header': h, 'header_format': fmt['head']} for h in headers]
    })
    sheet.set_row(4, 38)
    sheet.freeze_panes(5, 2)
    sheet.repeat_rows(0, 4)

def dropdown(sheet, first, col, last, values):
    sheet.data_validation(first, col, last, col, {
        'validate': 'list', 'source': values,
        'error_type': 'stop', 'error_title': 'Choose a listed value',
        'error_message': 'Use the dropdown so the scoring formulas can interpret the review.',
        'input_title': 'Reviewer input', 'input_message': 'Choose a value from the list.'
    })

runbooks = {}
for path in sorted((ROOT / 'runbooks').glob('RB-*.md')):
    text = path.read_text()
    rb = path.name[:6]
    blob = f'blob {len(text.encode())}\0'.encode() + text.encode()
    runbooks[rb] = {'path': path, 'text': text,
                    'sha': hashlib.sha1(blob).hexdigest(),
                    'url': 'https://github.com/mahesh-ai-architect/Second-Responder/blob/main/runbooks/' + path.name}

baseline = [
    ('RB-001', 'payments-api', 'payments-api /charge returns 5xx errors and Stripe requests time out. What should I check, what conditional remediation applies, and when should I escalate?'),
    ('RB-002', 'payments-api', 'The webhooks-inbound queue is above 10,000 and rising, with delivery failures going to the DLQ. What should I check, how should I recover, and when should I escalate?'),
    ('RB-003', 'auth-service', 'SSO login success is below 90%, with SAML signature validation failures. What should I check, what remediation applies, and when should I escalate?'),
    ('RB-004', 'auth-service', 'Users are not receiving MFA push prompts and approval latency exceeds 60 seconds. What should I check, what workaround applies, and when should I escalate?'),
    ('RB-005', 'search', 'The indexer-nightly job is stalled and logs show mapper_parsing_exception. What should I check, how should I recover, and when should I escalate?'),
    ('RB-006', 'checkout', 'Checkout p99 is above 2.5 seconds after a deploy and promo validation dominates traces. What should I check, what remediation applies, and how should I verify recovery?'),
    ('RB-007', 'notifications', 'Email queues are backing up and the provider returns 429 provider rate limit exceeded. What should I check, what remediation applies, and when should I escalate?'),
    ('RB-008', 'database-primary', 'Replica lag is above 30 seconds and climbing while a backfill runs. What should I check, what remediation conditions apply, and when should I escalate?'),
    ('RB-009', 'database-primary', 'The orders database connection pool is saturated and requests are failing. What should I check first, what remediation should I follow, and when should I escalate?'),
    ('RB-010', 'cdn-edge', 'CDN cache hit ratio dropped below 70%, origin traffic tripled, and edge 503s appeared after a config push. What should I check and do?'),
    ('RB-011', 'inventory', 'Stock sync is failing with deadlock detected on sku_locks and oversell alerts are active. What should I check, how should I recover, and who should I notify?'),
    ('RB-012', 'all', 'For a SEV1 incident, what are the acknowledgement and update targets, who can downgrade severity, and what follow-up is required?'),
]

test_data = []
for rb, service, question in baseline:
    # Preserve source wording instead of inventing an ideal generated answer.
    body = runbooks[rb]['text']
    expected = re.sub(r'\A.*?\n\n', '', body, count=1, flags=re.S)
    test_data.append([f'T{len(test_data)+1:03}', 'Development', 'Baseline', service,
                      question, 'Answered', rb, expected, runbooks[rb]['url'],
                      'Engineer should verify service relevance, conditions, and required steps. Add RB-009 to expected sources if detailed pool remediation is requested across runbooks.'])

extras = [
    ('Boundary', 'database-primary', 'DB CPU is 65%. Does RB-009 permit a temporary 25% pool_size increase?', 'Answered', 'RB-009',
     'No. A temporary 25% pool_size increase is allowed only if DB CPU is below 60%. Do not authorize the increase at 65%.'),
    ('Boundary', 'database-primary', 'DB CPU is exactly 60%. Does RB-009 permit a temporary 25% pool_size increase?', 'Answered', 'RB-009',
     'No. The condition is below 60%, not at or below 60%.'),
    ('Boundary', 'database-primary', 'DB CPU is 55%. What temporary pool_size increase does RB-009 allow?', 'Answered', 'RB-009',
     'Temporary pool_size increase of 25% is allowed only if DB CPU is below 60%. Do not invent a duration or a higher increase.'),
    ('Escalation', 'database-primary', 'Connection pool exhaustion has recurred twice in 24 hours. Who should I escalate to and what severity applies?', 'Answered', 'RB-009',
     'Escalate to the DB lead; treat as SEV2. This is a leak hunt.'),
    ('Conditional', 'payments-api', 'payments-api has 503s with no healthy upstream. Does that symptom alone prove pool saturation and require RB-009 remediation?', 'Answered', 'RB-001',
     'No. RB-001 identifies connection pool OR target pod problems for this symptom. Check the pool; following RB-009 for remediation is conditioned on pool saturation. Do not assert a confirmed diagnosis.'),
    ('Unsupported', 'outside corpus', 'Give me the exact GPU reset command for a video-transcoding service whose workers have stopped.', 'Clarification or abstention', '',
     'No video-transcoding runbook is in this corpus. Ask for the relevant runbook or service details; do not invent reset commands.'),
    ('Unsupported', 'outside corpus', 'What command should I run to repair a Kafka controller quorum failure?', 'Clarification or abstention', '',
     'No Kafka controller repair procedure is in this corpus. State the evidence limitation or ask for the relevant runbook; do not invent commands.'),
    ('Ambiguous', 'unknown', 'It is failing. What should I restart?', 'Clarification or abstention', '',
     'Ask for the affected service and exact alert or symptoms. Do not recommend an arbitrary restart.'),
]
for kind, service, question, outcome, rb, expected in extras:
    test_data.append([f'T{len(test_data)+1:03}', 'Development', kind, service, question,
                      outcome, rb, expected, runbooks[rb]['url'] if rb else '',
                      'Reviewer-authored starter expectation. Verify against source snapshots before using as a reference.'])

banner(guide, 'Second Responder | Evaluation workbook',
       '20 starter cases across 12 runbooks. No chatbot answers or scores are pre-filled. Blue text = editable input; gray cells = formulas.', 5)
guide.set_column('A:A', 5)
guide.set_column('B:F', 20)
instructions = [
    ('1  Review the test cases', 'Open Test Cases. Confirm the expected behavior with the runbook owner before testing. All starter cases are Development; add representative unseen Held-out cases for final assessment.'),
    ('2  Run a question in n8n', 'Use the existing chat workflow. In Responses, use its pre-filled Run ID and Test ID, paste Format Evidence output into Retrieved evidence, and paste the actual LLM answer into Answer.'),
    ('3  Record the outcome', 'Choose Answered, Clarification, Abstained, or Error. Set Response appropriate? by comparing with the expected behavior: useful and sufficient for answerable cases, or a justified clarification/abstention for unsupported cases.'),
    ('4  Review every atomic claim', 'In Claim Review, add one row per factual claim, using the matching Run ID. Separate commands, conditions, thresholds, and escalation rules. Keep an action connected to its prerequisite. Paste the exact supporting excerpt from the evidence actually retrieved for this run.'),
    ('5  Complete the verdicts', 'Faithfulness verdict: Supported, Unsupported, or Contradicted. Citation verdict: Supported, Wrong citation, or Missing citation. A claim can be supported somewhere in context but have a wrong citation. Set Critical error? to Yes for an unsupported command, remediation condition, or escalation threshold. Enter your reviewer name.'),
    ('6  Confirm coverage of the answer', 'In Responses, set Claim inventory complete? to Yes only after checking that every factual claim was listed. Mark this even for a genuine zero-claim clarification. Enter the response reviewer. Incomplete reviews receive no score.'),
    ('7  Read the dashboard', 'Faithfulness = supported claims / all claims, calculated only after the review is complete. The headline is the mean of scored responses. Claim-free responses are N/A and excluded; outcome and appropriateness counts are shown separately to prevent abstention from hiding poor usefulness.'),
    ('8  Iterate and reserve a final test set', 'Fix Development failures, then assess untouched Held-out questions. Use a fresh Run ID when retesting. Filter Responses by model/prompt/corpus version for fair comparisons. Dashboard aggregates every recorded run and is not a confidence guarantee.'),
    ('What PASS means', 'A reviewed response is appropriate, has no citation errors or critical operational errors, and reaches the target if it contains claims. This is a manual-review result on this example, not proof of future behavior or confirmation that the runbook itself is operationally correct.'),
    ('Scoring scope', 'Grade only against the saved retrieved context, not general model knowledge or runbooks absent from that context. Supporting a claim somewhere in the corpus is insufficient. If a runbook changes, retain the old retrieved evidence and corpus version for reproducibility.'),
    ('Using Google Sheets', 'Upload the .xlsx to Google Drive, open it with Google Sheets, and optionally save as Google Sheets. The workbook uses standard formulas. Check the Worked Example after import; formatting and table filters may differ.'),
    ('Capacity and reference data', 'Prepared for 200 cases, 200 response runs, and 2,000 claim rows. Stay inside these prepared rows; extending beyond them requires extending formulas and summary ranges. Runbook Reference contains local snapshots and file blob SHAs, not commit SHAs. GitHub links point to main and may change.'),
]
for index, (title, body) in enumerate(instructions):
    row = 4 + index * 3
    guide.merge_range(row, 1, row, 5, title, fmt['section'])
    guide.merge_range(row + 1, 1, row + 2, 5, body, fmt['body'])
    guide.set_row(row + 1, 27)
    guide.set_row(row + 2, 27)
guide.write_url(42, 1, 'https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/', fmt['link'], 'Ragas: faithfulness definition')
guide.write_url(43, 1, 'https://developers.openai.com/api/docs/guides/evaluation-best-practices', fmt['link'], 'Evaluation best practices')
guide.freeze_panes(4, 0)
guide.print_area(0, 0, 43, 5)

case_headers = ['Test ID', 'Split', 'Category', 'Service', 'Question', 'Expected outcome',
                'Expected runbooks', 'Expected key points / source wording', 'Source URL', 'Reviewer notes']
banner(cases, 'Test cases | Define expected behavior first',
       'Starter expectations are drawn from local runbook snapshots. All 20 cases are Development. Add unseen cases and label them Held-out before final assessment.', 9)
table(cases, 'TestCases', case_headers, CASE_LIMIT)
cases.set_column('A:C', 17, fmt['input'])
cases.set_column('D:D', 22, fmt['input'])
cases.set_column('E:E', 62, fmt['input'])
cases.set_column('F:G', 25, fmt['input'])
cases.set_column('H:H', 85, fmt['input'])
cases.set_column('I:J', 45, fmt['input'])
for idx, data in enumerate(test_data, 5):
    cases.set_row(idx, 120)
    for col, value in enumerate(data):
        if col == 8 and value:
            cases.write_url(idx, col, value, fmt['link'], value)
        else:
            cases.write_string(idx, col, value, fmt['input'])
dropdown(cases, 5, 1, 4 + CASE_LIMIT, ['Development', 'Held-out'])
dropdown(cases, 5, 5, 4 + CASE_LIMIT, ['Answered', 'Clarification or abstention'])

banner(refs, 'Runbook reference | Source snapshots',
       'These are local corpus snapshots, not evidence automatically retrieved by n8n. For faithfulness scoring, use the actual retrieved text saved with each response.', 4)
table(refs, 'RunbookSnapshots', ['Runbook ID', 'Filename', 'GitHub source', 'File blob SHA', 'Snapshot text'], len(runbooks))
refs.set_column('A:A', 14)
refs.set_column('B:B', 46)
refs.set_column('C:C', 48)
refs.set_column('D:D', 44)
refs.set_column('E:E', 110, fmt['body'])
for row, (rb, source) in enumerate(runbooks.items(), 5):
    refs.set_row(row, 320)
    refs.write(row, 0, rb)
    refs.write(row, 1, source['path'].name)
    refs.write_url(row, 2, source['url'], fmt['link'], 'Open GitHub runbook')
    refs.write(row, 3, source['sha'])
    refs.write_string(row, 4, source['text'], fmt['body'])

claim_headers = ['Run ID', 'Claim ID', 'Atomic claim / action plus conditions', 'Cited source IDs',
                 'Exact supporting excerpt from retrieved evidence', 'Faithfulness verdict',
                 'Citation verdict', 'Critical error?', 'Reviewer', 'Notes / correction', 'Review complete']
banner(claims, 'Claim review | One factual claim per row',
       'Use the Run ID from Responses. Judge faithfulness against saved retrieved context; judge citation support against the specific cited source. Complete all verdicts and reviewer.', 10)
table(claims, 'Claims', claim_headers, CLAIM_LIMIT)
claims.set_column('A:B', 15, fmt['input'])
claims.set_column('C:C', 65, fmt['input'])
claims.set_column('D:D', 18, fmt['input'])
claims.set_column('E:E', 70, fmt['input'])
claims.set_column('F:I', 22, fmt['input'])
claims.set_column('J:J', 45, fmt['input'])
claims.set_column('K:K', 20, fmt['formula'])
dropdown(claims, 5, 5, 4 + CLAIM_LIMIT, ['Supported', 'Unsupported', 'Contradicted', 'Not reviewed'])
dropdown(claims, 5, 6, 4 + CLAIM_LIMIT, ['Supported', 'Wrong citation', 'Missing citation', 'Not reviewed'])
dropdown(claims, 5, 7, 4 + CLAIM_LIMIT, ['Yes', 'No', 'Not reviewed'])
for row in range(5, 5 + CLAIM_LIMIT):
    n = row + 1
    formula = (f'=IF(OR(A{n}="",C{n}=""),"",IF(AND('
               f'COUNTIF(Responses!$A$6:$A${RUN_LIMIT+5},A{n})=1,'
               f'B{n}<>"",COUNTIFS($A$6:$A${CLAIM_LIMIT+5},A{n},$B$6:$B${CLAIM_LIMIT+5},B{n})=1,'
               f'OR(F{n}="Supported",F{n}="Unsupported",F{n}="Contradicted"),'
               f'OR(G{n}="Supported",G{n}="Wrong citation",G{n}="Missing citation"),'
               f'OR(H{n}="Yes",H{n}="No"),I{n}<>"",'
               f'OR(F{n}<>"Supported",E{n}<>""),'
               f'OR(G{n}<>"Supported",AND(F{n}="Supported",D{n}<>"",E{n}<>""))),"Yes","No"))')
    claims.write_formula(row, 10, formula, fmt['formula'], '')
claims.conditional_format(5, 5, 4 + CLAIM_LIMIT, 5, {'type': 'text', 'criteria': 'containing', 'value': 'Unsupported', 'format': fmt['bad']})
claims.conditional_format(5, 5, 4 + CLAIM_LIMIT, 5, {'type': 'text', 'criteria': 'containing', 'value': 'Contradicted', 'format': fmt['bad']})
claims.conditional_format(5, 7, 4 + CLAIM_LIMIT, 7, {'type': 'cell', 'criteria': '==', 'value': '"Yes"', 'format': fmt['bad']})

response_headers = ['Run ID', 'Test ID', 'Split', 'Question', 'Run timestamp', 'Model',
                    'Prompt / workflow version', 'Corpus version / namespace', 'Retrieved evidence (full text)',
                    'Answer (JSON or text)', 'Outcome', 'Response appropriate?', 'Citation errors',
                    'Critical errors', 'Total claims', 'Supported claims', 'Unreviewed claims',
                    'Faithfulness', 'Review status', 'Reviewer', 'Notes', 'Expected runbooks',
                    'Expected behavior', 'Claim inventory complete?']
banner(runs, 'Responses | Paste actual n8n evidence and answer',
       '20 Run IDs and Test IDs are prepared. No scores are fabricated. Fill the answer, evidence, outcome, appropriateness, reviewer, and claim inventory confirmation; grade atomic claims in Claim Review.', 23)
table(runs, 'Responses', response_headers, RUN_LIMIT)
runs.set_column('A:B', 14, fmt['input'])
runs.set_column('C:C', 17, fmt['formula'])
runs.set_column('D:D', 55, fmt['formula'])
runs.set_column('E:H', 24, fmt['input'], {'hidden': True, 'level': 1})
runs.set_column('I:J', 68, fmt['input'])
runs.set_column('K:L', 23, fmt['input'])
runs.set_column('M:Q', 15, fmt['formula'])
runs.set_column('R:R', 17, fmt['percent'])
runs.set_column('S:S', 25, fmt['formula'])
runs.set_column('T:T', 20, fmt['input'])
runs.set_column('U:U', 40, fmt['input'])
runs.set_column('V:W', 55, fmt['formula'])
runs.set_column('X:X', 25, fmt['input'])
runs.set_column('I:I', 68, fmt['input'], {'collapsed': True})
dropdown(runs, 5, 10, 4 + RUN_LIMIT, ['Answered', 'Clarification', 'Abstained', 'Error'])
dropdown(runs, 5, 11, 4 + RUN_LIMIT, ['Yes', 'No', 'Not reviewed'])
dropdown(runs, 5, 23, 4 + RUN_LIMIT, ['Yes', 'No'])
case_range = f"'Test Cases'!$A$6:$J${CASE_LIMIT+5}"
cr = {col: f"'Claim Review'!${col}$6:${col}${CLAIM_LIMIT+5}" for col in 'ACFGHK'}
for row in range(5, 5 + RUN_LIMIT):
    n = row + 1
    if row - 5 < len(test_data):
        idx = row - 5
        runs.write_string(row, 0, f'R{idx+1:03}', fmt['input'])
        runs.write_string(row, 1, test_data[idx][0], fmt['input'])
        runs.set_row(row, 85)
    for col, index in [(2, 2), (3, 5), (21, 7), (22, 8)]:
        cached = test_data[row-5][index-1] if row-5 < len(test_data) else ''
        runs.write_formula(row, col, f'=IF(B{n}="","",IFERROR(VLOOKUP(B{n},{case_range},{index},FALSE),"Unknown Test ID"))', fmt['formula'], cached)
    count = lambda extra: f'COUNTIFS({cr["A"]},A{n},{cr["C"]},"<>",{extra})'
    wrong_citations = count(cr['G'] + ',"Wrong citation"')
    missing_citations = count(cr['G'] + ',"Missing citation"')
    critical_errors = count(cr['H'] + ',"Yes"')
    supported = count(cr['F'] + ',"Supported"')
    reviewed = count(cr['K'] + ',"Yes"')
    runs.write_formula(row, 12, f'=IF(A{n}="","",{wrong_citations}+{missing_citations})', fmt['formula'], 0 if row-5 < len(test_data) else '')
    runs.write_formula(row, 13, f'=IF(A{n}="","",{critical_errors})', fmt['formula'], 0 if row-5 < len(test_data) else '')
    runs.write_formula(row, 14, f'=IF(A{n}="","",COUNTIFS({cr["A"]},A{n},{cr["C"]},"<>"))', fmt['formula'], 0 if row-5 < len(test_data) else '')
    runs.write_formula(row, 15, f'=IF(A{n}="","",{supported})', fmt['formula'], 0 if row-5 < len(test_data) else '')
    runs.write_formula(row, 16, f'=IF(A{n}="","",O{n}-{reviewed})', fmt['formula'], 0 if row-5 < len(test_data) else '')
    score = (f'=IF(AND(A{n}<>"",COUNTIF($A$6:$A${RUN_LIMIT+5},A{n})=1,'
             f'COUNTIF(\'Test Cases\'!$A$6:$A${CASE_LIMIT+5},B{n})=1,'
             f'I{n}<>"",J{n}<>"",OR(K{n}="Answered",K{n}="Clarification",K{n}="Abstained"),'
             f'X{n}="Yes",T{n}<>"",O{n}>0,Q{n}=0),P{n}/MAX(1,O{n}),"")')
    runs.write_formula(row, 17, score, fmt['percent'], '')
    status = (f'=IF(A{n}="","",IF(AND(J{n}="",K{n}=""),"Pending",'
              f'IF(COUNTIF($A$6:$A${RUN_LIMIT+5},A{n})<>1,"Duplicate Run ID",'
              f'IF(COUNTIF(\'Test Cases\'!$A$6:$A${CASE_LIMIT+5},B{n})<>1,"Check Test ID",'
              f'IF(K{n}="Error","FAIL",IF(OR(I{n}="",J{n}=""),"Needs evidence / answer",'
              f'IF(NOT(OR(K{n}="Answered",K{n}="Clarification",K{n}="Abstained")),"Choose outcome",'
              f'IF(X{n}<>"Yes","Confirm claim inventory",IF(AND(K{n}="Answered",O{n}=0),"Needs claims",'
              f'IF(Q{n}>0,"Needs claim review",IF(OR(NOT(OR(L{n}="Yes",L{n}="No")),T{n}=""),"Needs response review",'
              f'IF(OR(L{n}="No",M{n}>0,N{n}>0,AND(ISNUMBER(R{n}),R{n}<Dashboard!$B$5)),"FAIL","PASS"))))))))))))')
    runs.write_formula(row, 18, status, fmt['formula'], 'Pending' if row-5 < len(test_data) else '')
runs.conditional_format(5, 18, 4 + RUN_LIMIT, 18, {'type': 'cell', 'criteria': '==', 'value': '"PASS"', 'format': fmt['good']})
runs.conditional_format(5, 18, 4 + RUN_LIMIT, 18, {'type': 'cell', 'criteria': '==', 'value': '"FAIL"', 'format': fmt['bad']})
runs.conditional_format(5, 17, 4 + RUN_LIMIT, 17, {'type': '3_color_scale', 'min_value': 0, 'mid_value': 0.9, 'max_value': 1, 'min_type': 'num', 'mid_type': 'num', 'max_type': 'num', 'min_color': '#F5B6B0', 'mid_color': '#FFF3D6', 'max_color': '#B7E1CD'})

banner(dash, 'Evaluation dashboard | Evidence before confidence',
       'Mean faithfulness uses completely reviewed responses with claims. No answers have been scored yet. Results describe recorded tests, not guaranteed production performance.', 5)
dash.set_column('A:A', 42)
dash.set_column('B:B', 22)
dash.set_column('C:C', 4)
dash.set_column('D:F', 22)
dash.write('A5', 'Faithfulness target (editable)', fmt['section'])
dash.write_number('B5', 0.9, fmt['input_pct'])
dash.data_validation('B5', {'validate': 'decimal', 'criteria': 'between', 'minimum': 0, 'maximum': 1})
rr = lambda col: f"Responses!${col}$6:${col}${RUN_LIMIT+5}"
metrics = [
    ('Scored responses', f'=COUNT({rr("R")})', 0, 'big'),
    ('Mean faithfulness', f'=IF(COUNT({rr("R")})=0,"Not scored",AVERAGE({rr("R")}))', 'Not scored', 'big_pct'),
    ('Mean target reached?', f'=IF(COUNT({rr("R")})=0,"Not evaluated",IF(AVERAGE({rr("R")})>=B5,"Yes","No"))', 'Not evaluated', 'big'),
    ('PASS responses', f'=COUNTIF({rr("S")},"PASS")', 0, 'big'),
    ('FAIL responses', f'=COUNTIF({rr("S")},"FAIL")', 0, 'big'),
    ('Citation errors flagged', f'=SUM({rr("M")})', 0, 'big'),
    ('Critical operational errors flagged', f'=SUM({rr("N")})', 0, 'big'),
    ('Answered outcomes', f'=COUNTIF({rr("K")},"Answered")', 0, 'big'),
    ('Clarification / abstention outcomes', f'=COUNTIF({rr("K")},"Clarification")+COUNTIF({rr("K")},"Abstained")', 0, 'big'),
    ('Inappropriate responses flagged', f'=COUNTIF({rr("L")},"No")', 0, 'big'),
    ('Claims awaiting review', f'=SUM({rr("Q")})', 0, 'big'),
    ('Held-out scored responses', f'=SUMPRODUCT(--({rr("C")}="Held-out"),--ISNUMBER({rr("R")}))', 0, 'big'),
    ('Held-out mean faithfulness', f'=IF(B18=0,"Not scored",SUMIF({rr("C")},"Held-out",{rr("R")})/B18)', 'Not scored', 'big_pct'),
    ('Answered responses marked appropriate', f'=COUNTIFS({rr("K")},"Answered",{rr("L")},"Yes",Responses!$B$6:$B${RUN_LIMIT+5},"<>")', 0, 'big'),
]
# Metrics occupy rows 7..20; held-out scored count is B18.
for row, (label, formula, cached, style) in enumerate(metrics, 6):
    dash.write(row, 0, label, fmt['body'])
    dash.write_formula(row, 1, formula, fmt[style], cached)
    dash.set_row(row, 31)
dash.merge_range('A23:F25', 'A mean of 90% does not make an unsupported command acceptable. Review critical errors separately. Zero observed errors is evidence from these tests, not a guarantee. Examine individual cases and service-level failures; report appropriateness and abstention alongside faithfulness.', fmt['body'])
dash.merge_range('A27:F29', 'All starter tests are Development and no answers are pre-scored. Add unseen Held-out cases. Use unique Run IDs for retests and compare one prompt/model/corpus version at a time. This dashboard aggregates all rows, including repeated runs.', fmt['body'])
dash.freeze_panes(4, 0)
dash.print_area('A1:F29')

banner(example, 'Worked example | Illustration only',
       'These sample scores demonstrate the math. They are NOT chatbot results and are excluded from the Dashboard. Check this sheet after importing into Google Sheets.', 5)
example.set_column('A:A', 36)
example.set_column('B:D', 19)
example.set_column('E:F', 35)
example.write_row('A5', ['Illustration', 'Supported claims', 'Total claims', 'Faithfulness', 'Interpretation'], fmt['head'])
illustrations = [('One unsupported claim', 9, 10, '90% is below perfect; inspect what was unsupported.'),
                 ('All claims supported', 4, 4, '100% for this illustrative answer only.'),
                 ('No factual claims', 0, 0, 'N/A; separately assess whether abstaining was appropriate.')]
for row, (label, supported, total, note) in enumerate(illustrations, 5):
    n = row + 1
    example.write(row, 0, label, fmt['body'])
    example.write_number(row, 1, supported, fmt['input'])
    example.write_number(row, 2, total, fmt['input'])
    example.write_formula(row, 3, f'=IF(C{n}=0,"N/A",B{n}/C{n})', fmt['percent'], supported / total if total else 'N/A')
    example.write(row, 4, note, fmt['body'])
    example.set_row(row, 48)
example.merge_range('A11:F12', 'Claim splitting: “Increase pool_size by 25% only if CPU is below 60%” is one conditional action. Removing or broadening its prerequisite changes its meaning and must be treated as an unsupported operational claim.', fmt['body'])
example.merge_range('A14:F15', 'A numbered step may contain multiple claims. For example, an escalation destination and its severity threshold can require separate checks. Do not count numbered steps as if they were always atomic claims.', fmt['body'])
example.print_area('A1:F15')

guide.activate()
book.close()
print(DEST)
print(f'{len(test_data)} starter test cases; {len(runbooks)} source snapshots; no real results pre-scored.')
