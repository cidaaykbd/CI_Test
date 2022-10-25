#Import needed libraries
import time
from bs4 import BeautifulSoup as bs
import requests as rq
import pygal
import pygal
from IPython.display import display, HTML

base_html = """
<!DOCTYPE html>
<html>
  <head>
  <script type="text/javascript" src="http://kozea.github.com/pygal.js/javascripts/svg.jquery.js"></script>
  <script type="text/javascript" src="https://kozea.github.io/pygal.js/2.0.x/pygal-tooltips.min.js""></script>
  </head>
  <body>
    <figure>
      {rendered_chart}
    </figure>
  </body>
</html>
"""


#define functions for data collection
def find_book_name(table):
    if table.find('caption'):
        name = table.find('caption')
    return name.text

def get_author(table):
    author_name = table.find(text='Author').next.text
    return author_name

def get_genre(table):
    if table.find(text='Genre'):
        genre = table.find(text='Genre').next.text
    else:
        genre = table.find(text='Subject').next.next.next.text 
    return genre

def get_publishing_date(table):
    if table.find(text='Publication date'):
        date = table.find(text='Publication date').next.text
    else:
        date = table.find(text='Published').next.text
    pattern = re.compile(r'\d{4}')
    year = re.findall(pattern, date)[0]
    return int(year)

def get_pages_count(table):
    pages = table.find(text='Pages').next.text
    return int(pages)

def parse_wiki_page(url):
    page = rq.get(url).text
    return bs(page)

def get_book_info_robust(book_url):
    #To avoid breaking the code
    try:
        book_soup = parse_wiki_page(book_url)
        book_table = book_soup.find('table',class_="infobox vcard")
    except:
        print(f"Cannot parse table: {book_url}")
        return None
    
    book_info = {}
    #get info with custom functions
    values = ['Author', 'Book Name', 'Genre', 
            'Publication Year', 'Page Count']
    functions = [get_author, find_book_name, get_genre,
               get_publishing_date, get_pages_count]

    for val, func in zip(values, functions):
        try:
            book_info[val] = func(book_table)
        except:
            book_info[val] = None

    return book_info
#Get books
url = 'https://en.wikipedia.org/wiki/Science_Fiction:_The_100_Best_Novels'


page = rq.get(url).text
soup = bs(page)
table = soup.find('table', class_="wikitable")
if table is None:
    #handle something here when table is not present in your html.
    print("table is empty")
    print(table)
else:
    rows=  table.find_all('tr')[1:]
    books_links = [row.find('a')['href'] for row in rows]
    print(books_links)
    base_url = 'https://en.wikipedia.org'
    books_urls = [base_url + link for link in books_links]
    #to store books info
    book_info_list = []
    #loop first books
    for link in books_urls:
    #get book info
        book_info = get_book_info_robust(link)
        #if everything is correct and no error occurs
        if book_info:
            book_info_list.append(book_info)
        #puase a second between each book
        time.sleep(1)
        
        #Collect different genres
        genres = {}
        for book in book_info_list:
            book_gen = book['Genre']
            if book_gen:
                if 'fiction' in book_gen or 'Fiction' in book_gen:
                    book_gen = 'fiction'
            if book_gen not in genres: #count books in each genre
                genres[book_gen] = 1
            else:
                genres[book_gen] += 1
                
        print(genres)
        #Plot results
        bar_chart = pygal.Bar(height=400)
        [bar_chart.add(k,v) for k,v in genres.items()]
        display(HTML(base_html.format(rendered_chart=bar_chart.render(is_unicode=True))))
        html = base_html.format(rendered_chart=bar_chart.render(is_unicode=True))

        with open('index.html', 'w') as f:
            f.write(html)
  
