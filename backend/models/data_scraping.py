import requests
from bs4 import BeautifulSoup
import time
MAIN_URL = 'https://my.uq.edu.au/programs-courses/browse.html?level=ugpg'

response = requests.get(MAIN_URL)
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table')
print("Test")

headers = []
for th in table.find_all('th'):
    headers.append(th.text.strip())
    break

print(headers)
# table_data = []
# for row in table.find_all('tr'):
#     current_row = []
#     for td in row.find_all('td'):
#         current_row.append(td.text.strip())
#     if current_row:
#         table_data.append(current_row)
#     print(current_row)
#     break


# print("Headers:", headers)
# for row_data in table_data:
#     print(row_data)