import requests
import pandas as pd
from bs4 import BeautifulSoup


class WikiTableParser:
    def __init__(self, urls):
        if isinstance(urls, str):
            urls = [urls]
        elif not isinstance(urls, list):
            raise TypeError("URLs should be a string or a list of strings.")
        self.urls = urls
        self.soup_list = []
        self.tables_list = []

    def fetch_pages(self):
        for url in self.urls:
            response = requests.get(url)
            response.raise_for_status()  # Ensure the request was successful
            soup = BeautifulSoup(response.text, 'html.parser')
            self.soup_list.append(soup)
            self.tables_list.append(soup.find_all('table', {'class': 'wikitable'}))

    def parse_table(self, url_index, table_index):
        if not self.tables_list:
            raise ValueError("No tables found. Please ensure the pages are fetched successfully.")
        if url_index >= len(self.tables_list):
            raise IndexError("URL index out of range.")
        if table_index >= len(self.tables_list[url_index]):
            raise IndexError("Table index out of range for the specified URL.")

        table = self.tables_list[url_index][table_index]
        rows = table.find_all('tr')

        data = []
        headers = [header.get_text(strip=True) for header in rows[0].find_all('th')]

        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) == 0:
                continue

            row_data = [cell.get_text(strip=True).replace('N/A', '0') for cell in cells]
            data.append(row_data)

        return pd.DataFrame(data, columns=headers)

    def parse_tables(self, url_indexes, table_indexes):
        if isinstance(url_indexes, int):
            url_indexes = [url_indexes]
        elif not isinstance(url_indexes, list):
            raise TypeError("URL indexes should be an integer or a list of integers.")

        if isinstance(table_indexes, int):
            table_indexes = [table_indexes]
        elif not isinstance(table_indexes, list):
            raise TypeError("Table indexes should be an integer or a list of integers.")

        parsed_tables = {}
        for url_index in url_indexes:
            for table_index in table_indexes:
                df = self.parse_table(url_index, table_index)
                table_name = f"url_{url_index}_table_{table_index}"
                parsed_tables[table_name] = df

        return parsed_tables


# Example usage
if __name__ == "__main__":
    urls = [
        "https://en.wikipedia.org/wiki/Storage_Wars_season_1",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_2",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_3",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_4",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_5",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_6",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_7",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_8",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_9",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_10",
        "https://en.wikipedia.org/wiki/Storage_Wars_season_11",
    ]

    parser = WikiTableParser(urls)
    parser.fetch_pages()

    # Parse a specific table from a specific URL
    table_df = parser.parse_table(0, 0)
    print(table_df)

    # Parse multiple tables across different URLs
    tables = parser.parse_tables([0, 1], [0])
    for table_name, df in tables.items():
        print(f"\n{table_name}:\n{df}")
