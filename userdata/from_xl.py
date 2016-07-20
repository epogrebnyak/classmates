import xlrd
import os

XL_PATH = os.path.join('userdata', 'classmates.xls')

def get_full_classlist():
    rb = xlrd.open_workbook(XL_PATH)
    sheet = rb.sheet_by_index(0)
    for rownum in range(sheet.nrows):
        row = sheet.row_values(rownum)
        yield(row)

def get_printable():
    for x in get_full_classlist():
        if x[0] and x[5]:
            name = ' '.join([x[0],x[1]])
            id = str(int(x[5]))
            yield name, id
            