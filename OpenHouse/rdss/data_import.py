from openpyxl import load_workbook
from rdss.models import Student
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

def ImportStudentCardID(file):
    wb = load_workbook(file)
    sheet = wb.worksheets[0]

    for i in range(2, sheet.max_row+1):
        Student.objects.get_or_create(idcard_no= sheet.cell(row=i, column=2).value, student_id=sheet.cell(row=i, column=1).value, name=sheet.cell(row=i, column=3).value )
