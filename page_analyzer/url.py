from urllib.parse import urlparse


def normalize_url(site: str) -> str:
    """
    Parse a URL
    :return: scheme://netloc
    """
    normalize = urlparse(site)
    home_page = f'{normalize.scheme}://{normalize.netloc}'
    return home_page
