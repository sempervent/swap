# swap/wikitableparser.py

from wikitableobject import WikiTableObject
from wikitableprocessor import WikiTableProcessor

class WikiTableParser:
    def __init__(self, url, table_index, season):
        self.wiki_table = WikiTableObject(url, table_index)
        self.season = season

    def parse_and_process(self):
        headers, data = self.wiki_table.parse_table()
        if headers and data:
            processor = WikiTableProcessor(headers, data, self.season)
            return processor.to_dataframe()
        return None
