import os
import jsonpickle

class WebSite:
    alias: str
    url: str
    xpath: str

    def __init__(self, a, u, x) -> None:
        self.alias = a
        self.url = u
        self.xpath = x

class Config:
    cache: str
    headers: dict[str, str]
    banwords: list[str]
    sites: list[WebSite]

    def __init__(self) -> None:
        self.cache = './cache/'
        self.headers = { 'User-Agent': 'replace-me/1.0' }
        self.banwords = ['the']
        self.sites = [
            WebSite('test', 'http://google.com', '//body/text()')
        ]

    def save(self, file: str) -> None:
        f = open(file, 'w', encoding='utf-8')
        f.write(jsonpickle.encode(self, indent=True))
        f.close()

    @staticmethod
    def load(file: str):
        if not os.path.exists(file):
            Config().save(file)
        f = open(file, 'r', encoding='utf-8')
        res = jsonpickle.decode(f.read())
        f.close()
        return res