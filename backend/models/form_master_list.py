import requests
from bs4 import BeautifulSoup
import time
import csv

MAIN_URL = 'https://my.uq.edu.au/programs-courses/browse.html?level=ugpg'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Fetch the webpage content
response = requests.get(MAIN_URL, headers=headers, verify=False)  # Setting verify to False skips SSL verification (Not recommended for production use!)

response.raise_for_status()

soup = BeautifulSoup(response.content, 'html.parser')

tables = soup.find_all('table')
tables = tables[1:]
table_data = []



for table in tables:
    rows_container = table.tbody if table.tbody else table
    current_title = None
    current_title_url = None

    for row in rows_container.find_all('tr'):
        title_cell = row.find('td', class_='title')
        plan_cell = row.find('td', class_='plan')
        type_cell = row.find('td', class_='type')
        
        title_url = title_cell.a['href'] if title_cell.a and (title_cell.a.href is not None) else None
        
        if 'letter' in row.get('class', []):

            current_title = title_cell.a.text.strip() if title_cell.a else title_cell.text.strip()
            current_title_url = title_url
            continue 

        if title_cell.a or title_cell.text.strip():
            current_title = title_cell.a.text.strip() if title_cell.a else title_cell.text.strip()
            current_title_url = title_url
        
        plan = plan_cell.a.text.strip() if plan_cell.a else plan_cell.text.strip()
        plan_url = plan_cell.a['href'] if plan_cell.a else None
        

        type_ = type_cell.text.strip()

        table_data.append([current_title, current_title_url, plan, plan_url, type_])


print("Headers:", headers)
for row_data in table_data:
    print(row_data)

with open('table_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    writer.writerows(table_data)