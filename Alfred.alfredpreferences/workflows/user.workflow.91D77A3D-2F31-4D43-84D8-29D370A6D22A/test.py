
import csv

from feedback import Feedback

query = '{query}'
query = query.lower()
baseurl = 'https://httpstatuses.com/'

fb = Feedback()

with open('status_code.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        code, desc = row
        lower_desc = desc.lower()

        if code.find(query) != -1:
            fb.add_item(desc, code, arg=baseurl + code)
        elif lower_desc.find(query) != -1:
            fb.add_item(code, desc, arg=baseurl + code)

print(fb)
