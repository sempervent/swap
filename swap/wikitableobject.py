# swap/wikitableobject.py

import requests
from bs4 import BeautifulSoup

class WikiTableObject:
    def __init__(self, url, table_index):
        self.url = url
        self.table_index = table_index
        self.table = None
        self.metadata = None
        self.fetch_table()

    def fetch_table(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table', {'class': 'wikitable'})
            if self.table_index >= len(tables):
                raise IndexError("Table index out of range.")
            self.table = tables[self.table_index]
            self.metadata = self.get_table_metadata()
        except Exception as e:
            self.table = None
            self.metadata = {"error": str(e)}

    def parse_table(self):
        try:
            rows = self.table.find_all('tr')
            headers = [header.get_text(strip=True) for header in rows[0].find_all('th')]
            data = []
            for i, row in enumerate(rows[1:], start=1):
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True).replace('N/A', '0') for cell in cells]
                if len(row_data) == len(headers):
                    data.append(row_data)
                else:
                    raise ValueError(f"Parsing issue at row {i}: {row_data}")
            return headers, data
        except Exception as e:
            print(f"Error parsing table at {self.url} index {self.table_index}: {str(e)}")
            return None, None

    def get_table_metadata(self):
        return {
            "url": self.url,
            "table_index": self.table_index,
            "description": f"Table {self.table_index} from {self.url}",
            "name": f"Table {self.table_index}"
        }
