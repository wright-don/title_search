# ###########
#   Setup - Import Packages and Modules & Create Driver and Browser
# #############
#OS
import os

# Time
import time

# CSV 
import csv

# Folder Path Setup
pwd = os.getcwd()

# Login Credentials
from decouple import config
USERNAME = config('USERNAME')
KEY = config('KEY')

# Excel Sheets
import csv

# ###########
#   Modules - Classes that contain functions used within code
# #############
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Beautiful Soup
from bs4 import BeautifulSoup
# # Login Module ( For Using Login Class )
# from modules.login import Login as login
# # Go To Homepage Module ( Making Company Search Query and Navigating to Homepage )
# from modules.go_to_homepage import GoToHomepage
# # Get Search Module 
# from modules.get_search import GetSearch
# # Get Search Module 
# from modules.collect import Collect

driver = Service('driver/chromedriver')
browser = webdriver.Chrome(service=driver)


# ###########
#   The Application 
# #############

# Setting up dynamic variables ( Ask which companies are we searching and what roles )
question = "How many companies are you looking up? Max 5 - Enter Here : "
answer1 = int(input(question)[:1])
default = 1

if answer1 > 5:
    final = default
else: 
    final = answer1


companies = []
search_terms = []

# collect companies
k = 0
while k < final:
    companies.append(input(
        f"Enter Companpy {k+1} : "
    ))
    k+=1

    
# collect terms
count = (int(input(
    "Please enter number of search terms. (Max 3) Enter Here : "
)))

if count > 3:
    query_number = 3
else:
    query_number = count

i = 0
while i < query_number:
    search_terms.append(input(
        f"Enter Search query {i+1} : "
    ))
    i+=1


# ###########
#   The Application 
# #############

# Set Excel Header Row
headers = ["Company", "Search Query", "Name",
           "Title", "Page Link", "Location", "Employee"]

with open('final_list.csv', 'a') as f:
    object = csv.writer(f)
    object.writerow(headers)
    f.close()



# Speed
slow = 5
moderate = 3
fast = 2 
delay = moderate


class Search():

    def __init__(self, browser, search_terms, speed, time):
        self.browser = browser
        self.search_terms = search_terms
        self.speed = speed
        self.time = time


    # Login
    def login(self, username, key):
        browser.get('https://www.linkedin.com/uas/login')
        elementID = self.browser.find_element(By.ID, 'username')
        elementID.send_keys(username)
        elementID = self.browser.find_element(By.ID, 'password')
        elementID.send_keys(key)
        elementID.submit()   


    # Go To Homepage Method
    def go_to_page(self, company):
        #  Every company search on linkedin will contain this url syntax or prefix
        linkedin_search_baseurl = "https://www.linkedin.com/search/results/companies/?keywords="

        # linkedin url's have a dynamic syntax, therefore in order to search for companies whose name contains more than one word, we will need to concatentate the individual words with linkedin's uniuqe syntax ('%20' is placed between each word)

        # split the company name so each word is given an index
        company_word_list = company.split()

        # we need to create a variable that will hold the dynamic suffix to our base linkedin company search url.
        url_ending = ""

        # if the company name is just one word, then the url_ending will simply be the name of the company
        if len(company_word_list) == 1:
            url_ending += company_word_list[0]

        # if the company name is longer than 1 word, the search url syntax will change - For this, we can run a loop over each word in the company name, and if the current word is not first, place '$20' before the word at that current word's index.
        else:
            url_ending = company_word_list[0]
            i = 1
            while i < len(company_word_list):
                # each time the loop is ran, a value with be added to url_ending variable we've created
                url_ending += "%20" + company_word_list[i]
                i += 1

        # Company Insights URL
        company_url = linkedin_search_baseurl + url_ending
        # Now that we've identified what the url ending should be for the unique company we're researching, we can now navigate to the corresponding LI search query results

        self.browser.get(company_url)
        self.browser.implicitly_wait(5)
        self.time.sleep(5)

        # Company Linkedin Page URL
        company_li_url = self.browser.find_element(By.XPATH,'//div[@class="entity-result__item"]//a').get_attribute('href')
        self.browser.get(company_li_url)
        self.time.sleep(4)
        for search_term in self.search_terms:
            self.get_search(company, search_term, company_li_url)

    def get_search(self, company, search_query, company_li_url):
        self.time.sleep(3) 
        #Navigate to company homepage by clicking on search query link. 
        #Use direct selenium to grab company employee search query page 
        company_search_query_page_parent_element = browser.find_element(
            By.CLASS_NAME, 'display-flex.mt2.mb1')
        company_search_query_page = company_search_query_page_parent_element.find_element(By.CLASS_NAME,
        'ember-view')
        company_search_query_page.click()
        self.time.sleep(5)
        search_query_url = str(self.browser.current_url)
        position = search_query_url.find('COMPANY_PAGE')
        base_emp_search_url = search_query_url[:position]
        route = f'{base_emp_search_url}FACETED_SEARCH&title={search_query}'
        self.browser.get(route)
        self.time.sleep(5)
        self.collect(company, search_query, company_li_url)    

    def collect(self, company, search_query, company_li_url):
        self.time.sleep(3)
        try:
            # Load page content using beautiful soup
            src = browser.page_source
            soup = BeautifulSoup(src)
            ul_tag = soup.find(
                'ul', {'class': 'reusable-search__entity-result-list list-style-none'})
            li_tags = ul_tag.find_all('li')
            print(len(li_tags))
            # Loop over each list item and collect data
            for li_tag in li_tags:
                # [Company, Search Query, Name, Title, Location, Employee ]
                # Find name and profile link ( Same element )
                name_parent = li_tag.find(
                    'span', {'class', 'entity-result__title-text t-16'})
                target_element = name_parent.find("a", href=True)
                name = target_element.get_text().strip()
                page_link = target_element['href']
                
                # Find title
                title = li_tag.find(
                    'div', {'class': 'entity-result__primary-subtitle t-14 t-black t-normal'}).get_text().strip()

                # Find location
                location = li_tag.find(
                    'div', {'class': 'entity-result__secondary-subtitle t-14 t-normal'}).get_text().strip()
                
                employee = [name, title, page_link, location]          
                data = [company, search_query, name, title, page_link, location, employee]
                print(employee)
                # writing to csv file 
                with open("final_list.csv", 'a') as csvfile: 
                    object = csv.writer(csvfile)
                    print("completed")
                    object.writerow(data)
                    print("completed2")
                    csvfile.close()
                    print("completed3")
        except:
            print('First collect try block failed')
            name = ""
            title= ""
            page_link= "page_not_found"
            location= ""
            employee= ""
            page_link = ""
            data = [company, search_query, name,
                    title, page_link, location, employee]
            # writing to csv file
            with open("final_list.csv", 'a') as csvfile:
                object = csv.writer(csvfile)
                object.writerow(data)
                csvfile.close()

        # Navigate back to company homepage 
        browser.get(company_li_url)
        self.time.sleep(3)


#Login
search = Search(browser, search_terms, moderate, time)
search.login(USERNAME,KEY)
for company in companies: 
    search.go_to_page(company)
    
browser.close()
