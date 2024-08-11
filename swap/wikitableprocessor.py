import pandas as pd
from bs4 import BeautifulSoup

class WikiTableProcessor:
    def __init__(self, html_content, season):
        self.html_content = html_content
        self.season = season

    def parse_html_table(self):
        """Parses the HTML content into a list of dictionaries."""
        soup = BeautifulSoup(self.html_content, 'html.parser')
        table = soup.find('table', {'class': 'wikitable'})
        rows = table.find_all('tr')

        headers = [header.get_text(strip=True) for header in rows[0].find_all('th')]
        data = []
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) == len(headers):
                row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(len(headers))}
                data.append(row_data)
        return data

    def process_table_data(self, data):
        """Transforms parsed data into a long-format DataFrame."""
        records = []
        for entry in data:
            episode = entry.get('#')
            title = entry.get('Title')
            air_date = entry.get('Air date')

            parties = ['Dave Hester', 'Jarrod Schulz/Brandi Passante', 'Darrell Sheets/Brandon Sheets', 'Barry Weiss']
            for party in parties:
                spent = entry.get(f'{party}\nSpent')
                profit = entry.get(f'{party}\nNet profit/loss')
                if spent is not None and profit is not None:
                    records.append({
                        'Season': self.season,
                        'Episode': episode,
                        'Title': title,
                        'Air Date': air_date,
                        'Party': party,
                        'Spent': self._convert_currency(spent),
                        'Profit': self._convert_currency(profit)
                    })

        return pd.DataFrame(records)

    def _convert_currency(self, value):
        """Converts currency strings to float."""
        try:
            return float(value.replace('$', '').replace(',', ''))
        except ValueError:
            return None

    def to_dataframe(self):
        """Main method to convert the HTML table to a pandas DataFrame."""
        data = self.parse_html_table()
        return self.process_table_data(data)

# Example Usage
if __name__ == "__main__":
    # html_content = ... # Insert the HTML content of the wikitable here.
    # processor = WikiTableProcessor(html_content, season=1)
    # df = processor.to_dataframe()
    # print(df)
    pass
