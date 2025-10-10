from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import requests



# Request the webpage
response = requests.get('https://www.techworld-with-nana.com/post/a-guide-of-how-to-get-started-in-it-in-2023-top-it-career-paths')
soup = BeautifulSoup(response.content, 'html.parser')

# Find and translate headers
headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
for header in headers:
    translated = GoogleTranslator(source='auto', target='es').translate(header.text)
    header.string = translated

# Save translated HTML
with open('translated_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())