import re
import requests
from bs4 import BeautifulSoup
import json

cache = {}
def hashable_cache(f):
    ### to allocate cache for each url
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

@hashable_cache
def get_first_paragraph(wikipedia_url, session):
    ### get first paragraph of all paragraphs from a wikipedia
    req_wiki_url = session.get(wikipedia_url)

    soup = BeautifulSoup(req_wiki_url.content, "html")
    for paragraph in soup.find_all("p"):
        if paragraph.find_all("b"):
            first_paragraph = paragraph.get_text()
            break
    
    first_paragraph = re.sub ('\[\d\]','',first_paragraph)
    first_paragraph = re.sub ('\(.*\)','',first_paragraph)
    return first_paragraph

def get_leaders():
    ### get leaders from each countries and add the first paragraph of the leader's wiki url into the dictionary of the leader himself.
    root_url = "https://country-leaders.herokuapp.com"
    country_url = root_url + "/countries"
    cookie_url = root_url + "/cookie"
    leaders_url = root_url + "/leaders"
    
    leaders_per_country = {}
    session = requests.Session()

    req_cookies = session.get(cookie_url)
    cookies =req_cookies.cookies
    req_countries = session.get(country_url, cookies=cookies)
    countries = req_countries.json()


    for country in countries:
        #print(countries_loop)
    
        req_leaders = session.get(leaders_url, cookies=cookies, params="country=" + country)
        print(req_leaders.status_code)
        if req_leaders.status_code == 403:
            req_countries = session.get(cookie_url)
            cookies =req_countries.cookies
            req_leaders =session.get(leaders_url, cookies=cookies, params="country=" +country)
        
        
        leaders_per_country[country] = req_leaders.json()
        leaders_in_one_country = leaders_per_country[country]
        
        for leader in range(len(leaders_in_one_country)):
            #print (leader_loop )
            internal_calc2 = get_first_paragraph(leaders_in_one_country[leader]['wikipedia_url'], session)
            leaders_in_one_country[leader]['first_paragraph_text'] =internal_calc2
            leaders_per_country[country] = leaders_in_one_country
                
    return leaders_per_country



def save(leaders_per_country):

    with open('./myproject1/leaders.json',"w") as file:
        json.dump(leaders_per_country, file)

    
leaders_per_country = get_leaders()
save(leaders_per_country)