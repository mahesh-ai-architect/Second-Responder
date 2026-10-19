"""Create a single-sheet, manual RAG evaluation log."""
from pathlib import Path
import xlsxwriter


output = Path(__file__).parent / 'Second-Responder-Simple-Eval.xlsx'
workbook = xlsxwriter.Workbook(output)
sheet = workbook.add_worksheet('Eval Log')
sheet.hide_gridlines(2)
sheet.freeze_panes(6, 0)
sheet.set_landscape()
sheet.fit_to_pages(1, 0)
sheet.repeat_rows(0, 5)

title = workbook.add_format({'bold': True, 'font_size': 20, 'font_color': '#16324F'})
instruction = workbook.add_format({'text_wrap': True, 'valign': 'vcenter', 'font_color': '#45566B'})
header = workbook.add_format({'bold': True, 'bg_color': '#16324F', 'font_color': 'white', 'text_wrap': True, 'valign': 'vcenter'})
editable = workbook.add_format({'font_color': '#1565C0', 'text_wrap': True, 'valign': 'top'})
count = workbook.add_format({'font_color': '#1565C0', 'num_format': '0', 'valign': 'top'})
score = workbook.add_format({'num_format': '0%', 'bg_color': '#F0F3F6', 'valign': 'top'})
critical = workbook.add_format({'bg_color': '#FDE9E7', 'font_color': '#A12622', 'bold': True})

sheet.merge_range('A1:H1', 'Second Responder — Simple Eval Log', title)
sheet.set_row(0, 32)
sheet.merge_range('A2:H3', 'One row per chatbot answer. Paste the question, answer, and actual retrieved evidence from n8n. Count individual factual claims, then enter supported claims and total claims. The percentage calculates automatically.', instruction)
sheet.set_row(1, 22)
sheet.set_row(2, 22)
sheet.merge_range('A4:H4', 'Example: 9 supported / 10 total = 90%. Mark Critical error = Yes for an unsupported command, remediation condition, or escalation threshold; that answer needs correction even if the score is 90% or higher. Zero-claim answers are N/A; explain whether clarification was appropriate in Notes.', instruction)
sheet.set_row(3, 40)

headers = ['Question', 'Chatbot answer', 'Retrieved evidence / sources', 'Supported claims',
           'Total claims', 'Faithfulness', 'Critical error?', 'Notes / what to fix']
sheet.add_table(5, 0, 35, 7, {
    'name': 'SimpleEval', 'style': 'Table Style Medium 2',
    'columns': [{'header': name, 'header_format': header} for name in headers],
})
sheet.set_row(5, 34)
sheet.set_column('A:A', 40, editable)
sheet.set_column('B:C', 54, editable)
sheet.set_column('D:E', 15, count)
sheet.set_column('F:F', 16, score)
sheet.set_column('G:G', 17, editable)
sheet.set_column('H:H', 40, editable)

for row in range(6, 36):
    n = row + 1
    sheet.set_row(row, 70)
    sheet.write_formula(row, 5,
        f'=IF(OR(D{n}="",E{n}=""),"",IF(E{n}=0,"N/A",D{n}/E{n}))', score, '')
    for col, formula in [
        (3, f'=OR(D{n}="",AND(ISNUMBER(D{n}),D{n}=INT(D{n}),D{n}>=0,OR(E{n}="",D{n}<=E{n})))'),
        (4, f'=OR(E{n}="",AND(ISNUMBER(E{n}),E{n}=INT(E{n}),E{n}>=0,OR(D{n}="",E{n}>=D{n})))'),
    ]:
        sheet.data_validation(row, col, row, col, {
            'validate': 'custom', 'value': formula, 'error_type': 'stop',
            'error_title': 'Check claim counts',
            'error_message': 'Enter nonnegative whole numbers. Supported claims cannot exceed total claims.',
        })

sheet.data_validation('G7:G36', {
    'validate': 'list', 'source': ['Yes', 'No'], 'error_type': 'stop',
    'input_title': 'Critical operational error?',
    'input_message': 'Yes = unsupported command, remediation condition, or escalation threshold. Leave blank until reviewed.',
})
sheet.conditional_format('G7:G36', {
    'type': 'cell', 'criteria': '==', 'value': '"Yes"', 'format': critical,
})
sheet.write_comment('C6', 'Paste the actual retrieved source text from Format Evidence, including source IDs. A GitHub link alone may change over time.')
sheet.write_comment('D6', 'Count claims supported by the retrieved evidence. One numbered step may contain several factual claims. Preserve the conditions attached to actions.')
sheet.write_comment('F6', 'Supported claims divided by total claims. Blank until both counts are entered. N/A if there are no factual claims. This score alone does not determine whether an answer is acceptable.')
sheet.print_area('A1:H36')
sheet.activate()
workbook.set_calc_mode('auto')
workbook.close()
print(output.resolve())
