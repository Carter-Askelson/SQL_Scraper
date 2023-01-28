import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import psycopg2


from pathlib import Path

global level
global browser


reset_spot = "#fas-nav-world"
membership_spot = " > div > div.stat-line.w-graph > div:nth-child(1) > div.key-box.key-box-a > h4"
congregation_spot = " > div > div.stat-line.w-graph > div:nth-child(1) > div.key-box.key-box-b > h4"
mission_spot = " > div > div.stat-line.w-graph > div:nth-child(2) > h4.weird-label > span:nth-child(1)"
temple_spot = " > div > div.stat-line.w-graph > div.stat-block.weird-label-holder.continent-temples-block > h4.weird-label > span:nth-child(1)"
family_spot = " > div > div.stat-line.w-graph > div.stat-block.fh-stat-block > div > div.gen-one > div.box > span"

id = []
continents = ("north-america", "south-america", "europe", "asia", "oceania", "africa")
membership = []   
congregation = []
mission = []   
temple = []
family = []


#starts program
def main():  
    set_up_site()      
    get_values()
    create_tables()
    insert_data(id,
                continents,
                membership,  
                congregation,
                mission, 
                temple,
                family)
    end_program()

    




#gets Address and Zip Code and runs those through get_owner_name() until all rows are updated
def get_values():
    
    global level
    level = 0
    regions = ("#fas-continents > li:nth-child(1) > a", "#fas-continents > li:nth-child(2) > a", "#fas-continents > li:nth-child(3) > a", "#fas-continents > li:nth-child(4) > a", "#fas-continents > li:nth-child(5) > a", "#fas-continents > li:nth-child(6) > a")
    
    while level != 6:
        current_spot = browser.find_element(By.CSS_SELECTOR, regions[level])
        current_spot.click()
        scrape_page(level)        
        current_spot = browser.find_element(By.CSS_SELECTOR, reset_spot)
        current_spot.click()  
        level += 1    
   

#opens up the website needed to scrape data from
def set_up_site():
    global browser
    browser = webdriver.Chrome(str(Path.cwd()) + "\\chromedriver")
    browser.get('https://newsroom.churchofjesuschrist.org/facts-and-statistics#')
    

#gets data from each page given and stores it in lists
def scrape_page(level):
    global browser
    data_value = 0

    id.append(level + 1)
    data_value = browser.find_element(By.CSS_SELECTOR, combiner(continents[level], membership_spot)).text
    membership.append(int(data_value.replace(',',"")))
    data_value = browser.find_element(By.CSS_SELECTOR, combiner(continents[level], congregation_spot)).text
    congregation.append(int(data_value.replace(',',"")))
    data_value = browser.find_element(By.CSS_SELECTOR, combiner(continents[level], mission_spot)).text
    mission.append(int(data_value.replace(',',"")))
    data_value = browser.find_element(By.CSS_SELECTOR, combiner(continents[level], temple_spot)).text
    temple.append(int(data_value.replace(',',"")))
    data_value = browser.find_element(By.CSS_SELECTOR, combiner(continents[level], family_spot)).text
    family.append(int(data_value.replace(',',"")))
   

#function forms the exact css selector needed
def combiner(continent, spot):
    return str("#fas-continent-stats-" + continent + spot)

#test for database connection
""" def connect():

    conn = psycopg2.connect(
        host = "localhost",
        database = "churchstats",
        user = "postgres",
        password="askels0n",
        port = 5433)
    cur = conn.cursor()

    cur.execute('SELECT version()')

    db_version = cur.fetchone()
    print(db_version)

    cur.close() """

#connects to postgres server and creates tables
def create_tables():

    commands = (
        """
        CREATE TABLE statistics (
            key_id INTEGER PRIMARY KEY,
            continent VARCHAR(255) NOT NULL,
            total_membership INTEGER NOT NULL,
            congregations INTEGER NOT NULL,
            missions INTEGER NOT NULL,
            temples INTEGER NOT NULL,
            family_history_centers INTEGER NOT NULL
        )
        """
    )

    conn = psycopg2.connect(
        host = "localhost",
        database = "churchstats",
        user = "postgres",
        password="askels0n",
        port = 5433)
    cur = conn.cursor()

    cur.execute(commands)
    conn.commit()
    cur.close()
    conn.close()
   
#Insert data values scraped from website into newly created postgres tables
def insert_data(id,
                continents,
                membership,  
                congregation,
                mission, 
                temple,
                family):

    insert_sql = """INSERT INTO statistics				
                        (key_id, continent, total_membership, congregations, missions, temples, family_history_centers)			
                    VALUES				
                        (%s,%s,%s,%s,%s,%s,%s)		
                 """

    conn = psycopg2.connect(
        host = "localhost",
        database = "churchstats",
        user = "postgres",
        password="askels0n",
        port = 5433)
    cur = conn.cursor()
    row = 0
    while row != 6:
        row_values = (id[row], continents[row], membership[row], congregation[row], mission[row], temple[row], family[row])
        cur.execute(insert_sql, (row_values))
        row += 1

    conn.commit()
    cur.close()
    conn.close()


#Finishes up and ends program
def end_program():
    browser.quit()
    #test to check proper table values
    """ print(id)
    print(continents)
    print(membership)
    print(congregation)
    print(mission)
    print(temple)
    print(family) 
    xval = ""
    xval = input("Looks Good?")"""
    #connect()
    sys.exit()


main()
