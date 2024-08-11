import requests
import pandas as pd
from bs4 import BeautifulSoup

class WikiTableObject:
    def __init__(self, url, table_index):
        self.url = url
        self.table_index = table_index
        self.table = None
        self.fetch_table()

    def fetch_table(self):
        response = requests.get(self.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', {'class': 'wikitable'})
        if self.table_index >= len(tables):
            raise IndexError("Table index out of range.")
        self.table = tables[self.table_index]

    def parse_table(self):
        rows = self.table.find_all('tr')
        headers = [header.get_text(strip=True) for header in rows[0].find_all('th')]
        data = []
        for row in rows[1:]:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True).replace('N/A', '0') for cell in cells]
            data.append(row_data)
        return pd.DataFrame(data, columns=headers)
