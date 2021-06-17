import constants, feedparser, requests
from bs4 import BeautifulSoup

# Object to hold article
class Article:
    def __init__(self):
        self.title = None
        self.date = None
        self.img_url = None
        self.img_hotlink = None
        self.img_hotlink_full = None
        self.text = None
        self.url = None

# Request TFA list from Wikipedia
def get_articles():
    # Get data from Wikipedia
    payload = {'action':'featuredfeed', 'feed':'featured'}
    res = requests.get(constants.api_url, params=payload)

    # Parse xml response
    data = feedparser.parse(res.text)
    articles = []

    # Extract article content
    for e in data.entries:
        # Build article list
        article = Article()
        date_length = len(e.published)
        article.date = e.published[:date_length-13]

        # Extract data from description
        raw = e.description
        (article.img_alt, 
        article.img_url, 
        article.img_hotlink, 
        article.img_hotlink_full, 
        article.title, 
        article.text, 
        article.url) = extract_article(raw)

        articles.append(article)

    return articles

# Extract article content from the raw HTML mess in description
def extract_article(raw):
    # Parse HTML in the description
    soup = BeautifulSoup(raw, 'html.parser')

    # Extract article image url
    image_alt = soup.select_one('img')['alt']
    image_file_url = soup.select_one('a')['href']
    image_url = constants.wiki_url + image_file_url

    # Hotlink directly to Wikipedia
    image_hotlink = constants.hotlink_url + image_file_url[11:] + '&width=240'
    image_hotlink_full = constants.hotlink_url + image_file_url[11:] + '&width=720'

    # Extract real article title
    paragraph = soup.select_one('p')
    title = paragraph.find_all('a')[-1]['title']

    # Extract article text
    text = paragraph.get_text().replace('\n', '')
    text_length = len(text)

    # Remove the '(Full article...)' string at the end
    text = text[:text_length-18]

    # Extract article url
    article_url = constants.wiki_url + paragraph.find_all('a')[-1]['href']

    return image_alt, image_url, image_hotlink, image_hotlink_full, title, text, article_url