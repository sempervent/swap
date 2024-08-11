# swap/tui.py

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Markdown, Static
from wikitableparser import WikiTableParser
import re

class WikiTableViewer(App):
    def __init__(self, urls, seasons=None):
        super().__init__()
        self.urls = urls
        self.seasons = seasons if seasons else self.extract_seasons_from_urls(urls)
        self.tables = {}
        self.data_dict = {}
        self.selected_url_index = 0
        self.selected_table_index = 0
        self.load_tables(self.selected_url_index)

    def extract_seasons_from_urls(self, urls):
        """Extract season numbers from URLs assuming they are the last number in the URL."""
        season_pattern = re.compile(r"(\d+)$")
        seasons = []
        for url in urls:
            match = season_pattern.search(url)
            if match:
                seasons.append(int(match.group(1)))
            else:
                seasons.append(None)  # Handle case where no season is found
        return seasons

    def compose(self) -> ComposeResult:
        self.metadata_view = Static()
        self.markdown_view = Markdown()
        yield Container(Vertical(self.metadata_view, self.markdown_view))

    def on_mount(self):
        self.update_table_view()

    def load_tables(self, url_index):
        try:
            url = self.urls[url_index]
            season = self.seasons[url_index]
            parser = WikiTableParser(url, self.selected_table_index, season)
            self.tables[(url, self.selected_table_index)] = parser
        except Exception as e:
            self.markdown_view.update(f"Error loading table: {str(e)}")

    def update_table_view(self):
        try:
            current_parser = self.tables.get((self.urls[self.selected_url_index], self.selected_table_index))
            if current_parser:
                df = current_parser.parse_and_process()
                if df is not None and not df.empty:
                    table_md = df.to_markdown(index=False)
                    self.markdown_view.update(table_md)
                else:
                    self.markdown_view.update("Failed to parse table or no data available.")
            metadata = {
                "url": self.urls[self.selected_url_index],
                "table_index": self.selected_table_index
            }
            added_status = "Already added" if self.is_table_added(metadata) else "Not added"
            self.metadata_view.update(f"URL: {metadata['url']}\nTable Index: {metadata['table_index']}\nStatus: {added_status}")
        except Exception as e:
            self.markdown_view.update(f"Error updating table view: {str(e)}")

    def is_table_added(self, metadata):
        return metadata['url'] in self.data_dict and metadata['table_index'] in self.data_dict[metadata['url']]

    def on_key(self, event):
        try:
            current_parser = self.tables.get((self.urls[self.selected_url_index], self.selected_table_index))
            if event.key == "a" and current_parser:
                df = current_parser.parse_and_process()
                metadata = {
                    "url": self.urls[self.selected_url_index],
                    "table_index": self.selected_table_index
                }
                url = metadata['url']
                table_index = metadata['table_index']
                if url not in self.data_dict:
                    self.data_dict[url] = {}
                self.data_dict[url][table_index] = df
                self.selected_table_index = (self.selected_table_index + 1) % len(self.tables)
                self.update_table_view()
            elif event.key == "s":
                self.selected_table_index = (self.selected_table_index + 1) % len(self.tables)
                self.update_table_view()
            elif event.key == "n":
                self.selected_table_index = (self.selected_table_index + 1) % len(self.tables)
                self.update_table_view()
            elif event.key == "p":
                self.selected_table_index = (self.selected_table_index - 1) % len(self.tables)
                self.update_table_view()
            elif event.key == "j":
                self.selected_url_index = (self.selected_url_index - 1) % len(self.urls)
                self.load_tables(self.selected_url_index)
                self.selected_table_index = 0  # Reset to the first table of the new URL
                self.update_table_view()
            elif event.key == "l":
                self.selected_url_index = (self.selected_url_index + 1) % len(self.urls)
                self.load_tables(self.selected_url_index)
                self.selected_table_index = 0  # Reset to the first table of the new URL
                self.update_table_view()
            elif event.key == "t" and current_parser:
                df = current_parser.parse_and_process()
                if df is not None and not df.empty:
                    table_md = df.to_markdown(index=False)
                    self.markdown_view.update(table_md)
                else:
                    self.markdown_view.update("Failed to parse table or no data available.")
        except Exception as e:
            self.markdown_view.update(f"Error processing key event: {str(e)}")

    def on_load(self):
        self.bind("q", "quit", description="Quit")
        self.bind("a", "add", description="Add Table")
        self.bind("s", "skip", description="Skip Table")
        self.bind("n", "next_table", description="Next Table")
        self.bind("p", "previous_table", description="Previous Table")
        self.bind("j", "previous_url", description="Previous URL")
        self.bind("l", "next_url", description="Next URL")
        self.bind("t", "show_table", description="Show Table")

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

    # seasons = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Optional, now auto-extracted if not provided

    app = WikiTableViewer(urls)
    app.run()
