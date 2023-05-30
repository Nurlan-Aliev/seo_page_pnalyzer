from bs4 import BeautifulSoup
from urllib.parse import urlparse


def parse_url(response):
    soup = BeautifulSoup(response.content, 'html.parser')

    h1 = soup.h1.text if soup.h1 else ''

    title = soup.title.text if soup.title.text else ''

    content = soup.find('meta', attrs={'name': 'description'})

    description = content.get('content') if content else ''

    return h1, title, description


def normalize_url(url: str) -> str:
    """
    Parse a URL
    :return: scheme://netloc
    """
    normalize = urlparse(url)
    home_page = f'{normalize.scheme}://{normalize.netloc}'
    return home_page
