# This file is excuted by crontab

import io
import csv
import requests
import datetime
from company.models import ChineseFundedCompany


url = 'https://gcis.nat.gov.tw/document/company_mainland.csv'

response = requests.get(url)

csv_bytes = response.content

str_file = io.StringIO(csv_bytes.decode('utf-8'), newline='\n')
    
reader = csv.reader(str_file)
next(reader)
for row_list in reader:
    try:
        chinese_funded_compnay = ChineseFundedCompany.objects.get(cid=row_list[1])
        # chinese funded comapny may only change name 
        if chinese_funded_compnay.name != row_list[2]:
            chinese_funded_compnay.name = row_list[2]
            chinese_funded_compnay.save()
    except ChineseFundedCompany.DoesNotExist:
        ChineseFundedCompany.objects.create(cid=row_list[1], name=row_list[2])

# Once the file is closed,
# any operation on the file (e.g. reading or writing) will raise a ValueError
str_file.close()

print("Updated at :",datetime.datetime.now())