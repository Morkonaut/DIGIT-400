from bs4 import BeautifulSoup
import requests

def pricecompare():
    

    # Lets see the current top 25 Steam games that are on sale
    url = 'https://store.steampowered.com/search/?specials=1'

    page = requests.get(url)
    # To see whether or not the page is available
    # page or page.status_code
    # 200 = available

    # To see all of the html on the page
    # page.text

    # Parsing the html 
    html = BeautifulSoup(page.text, 'html.parser')

    # To prettify
    # print(html.prettify())

    # Finding the html tags for the game titles and converting them into a usable string
    titles = str(html.find_all('span', class_='title'))
    # print(titles)

    # Cleaning it up a bit by cutting off the html and list brackets
    deals = titles.replace('<span class="title">', '').replace('</span>', '')[1:-1].split(", ")

    #Adding a little text
    #print("\nThe current top 25 discounted games on Steam.\n")
    # Printing the game deals
    #for d in deals:
        #print(d)
    return deals
#pricecompare()