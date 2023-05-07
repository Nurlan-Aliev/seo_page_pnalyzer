from bs4 import BeautifulSoup


def parse_url(response):
    soup = BeautifulSoup(response.content, 'html.parser')

    h1 = ''
    if soup.h1:
        h1 = soup.h1.text

    title = ''
    if soup.title.text:
        title = soup.title.text

    description = ''
    for i in soup.find_all('meta'):
        if i.get('name') == 'description':
            description = i.get('content')

    return h1, title, description
