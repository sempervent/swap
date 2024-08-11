from textual.app import App
from textual.widgets import Static, ScrollView
from textual import events
import pandas as pd
from bs4 import BeautifulSoup
import requests

from .wikitableobject import WikiTableObject


class WikiTableViewer(App):
    def __init__(self, urls):
        super().__init__()
        self.urls = urls
        self.tables = {}
        self.selected_url_index = 0
        self.selected_table_index = 0

    async def on_mount(self):
        # Load the first URL's tables by default
        await self.load_tables(self.selected_url_index)

    async def load_tables(self, url_index):
        url = self.urls[url_index]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', {'class': 'wikitable'})
        self.tables = {i: WikiTableObject(url, i) for i in range(len(tables))}
        self.update_table_view()

    def update_table_view(self):
        self.body = ScrollView()
        self.body.update(self.render_table(self.tables[self.selected_table_index].parse_table()))

    def render_table(self, df: pd.DataFrame):
        table_str = df.to_string(index=False)
        return Static(table_str)

    async def on_key(self, event: events.Key):
        if event.key == "j":
            self.selected_table_index = (self.selected_table_index + 1) % len(self.tables)
            self.update_table_view()
        elif event.key == "k":
            self.selected_table_index = (self.selected_table_index - 1) % len(self.tables)
            self.update_table_view()
        elif event.key == "h":
            self.selected_url_index = (self.selected_url_index - 1) % len(self.urls)
            await self.load_tables(self.selected_url_index)
        elif event.key == "l":
            self.selected_url_index = (self.selected_url_index + 1) % len(self.urls)
            await self.load_tables(self.selected_url_index)

    async def on_startup(self):
        self.body = ScrollView()
        await self.load_tables(self.selected_url_index)
        self.update_table_view()

    async def on_quit(self, event: events.Quit):
        await self.shutdown()

    async def on_load(self):
        await self.bind("q", "quit", "Quit")
        await self.bind("j", "next_table", "Next Table")
        await self.bind("k", "previous_table", "Previous Table")
        await self.bind("h", "previous_url", "Previous URL")
        await self.bind("l", "next_url", "Next URL")


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

    app = WikiTableViewer(urls)
    app.run()
