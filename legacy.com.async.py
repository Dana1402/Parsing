from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import re
import time
import csv
from selenium.webdriver import ActionChains
import asyncio

options_chrome = webdriver.ChromeOptions()

def save_csv(name_of_file, fields):
    """creates empty csv file with header fields"""
    with open(name_of_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(fields)

def expand_click(driver):
    """click button expand to see all tags-links"""

    # Open expand buttons to get all possible links
    expand_buttons = driver.find_elements(By.XPATH, "//button[text()='Expand']")

    if expand_buttons:
        for btn in expand_buttons:
            ActionChains(driver).scroll_to_element(btn).perform()
            btn.click()


def get_links(url):
    """gets all links for every state-living area,
        creates lists of areas and states"""

    with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()),options=options_chrome) as driver:
        driver.get(url)

        a_states = driver.find_elements(By.XPATH, "//a[@data-component='RegionsLink']")
        states_links = [state.get_attribute('href') for state in a_states]
        states_names = [state.find_element(By.XPATH, ".//button").text for state in a_states]
        states_list = []
        names_of_residence_total = []
        links_total = []

        for state_name, state_link in zip(states_names, states_links):
            print(state_name)
            driver.get(state_link)

            expand_click(driver)

            try:
                f_metro_area = driver.find_element(By.XPATH, "//a[@data-component='MetroAreaLink']")

                # Gather metro areas
                metro_areas = driver.find_elements(By.XPATH, "//a[@data-component='MetroAreaLink']")
                metro_links = [metro_area.get_attribute('href') for metro_area in metro_areas]
                names_of_residence = [metro_area.find_element(By.XPATH, "./button").text for metro_area in metro_areas]
            except:
                print(f'No metro_areas in {state_name}')

            f_county = driver.find_element(By.XPATH, "//a[@data-component='CountyLink']")

            counties = driver.find_elements(By.XPATH, "//a[@data-component='CountyLink']")
            counties_links = [county.get_attribute('href') for county in counties]
            counties_names = [county.find_element(By.XPATH, "./button").text for county in counties]

            f_city = driver.find_element(By.XPATH, "//a[@data-component='CityLink']")

            cities = driver.find_elements(By.XPATH, "//a[@data-component='CityLink']")
            city_links = [city.get_attribute('href') for city in cities]
            city_names = [city.find_element(By.XPATH, "./button").text for city in cities]

            links_total.extend(metro_links)
            links_total.extend(counties_links)
            links_total.extend(city_links)

            names_of_residence_total.extend(names_of_residence)
            names_of_residence_total.extend(counties_names)
            names_of_residence_total.extend(city_names)
            len_all_places = len(names_of_residence) + len(counties_names) + len(city_names)

            states_list.extend([state_name]*len_all_places)

            print(f'Number of living places in state {state_name}: ', len_all_places)

        return states_list, names_of_residence_total, links_total

def scroll_cards(driver, state, residence):
    """ scrolls cards,
        gets basic data from cards"""

    ActionChains(driver).scroll_by_amount(delta_x=0, delta_y=500).perform()
    time.sleep(1)
    try:
        modal = driver.find_element(By.XPATH, "//div[@data-component='ModalContainer']")
        modal.find_element(By.XPATH, "./button[@data-component='ModalCloseButton']").click()
    except:
        pass

    container_personCard = driver.find_element(By.XPATH, "//div[@class='Box-sc-ucqo0b-0 vDyOp']")
    while True:
        ActionChains(driver).scroll_to_element(container_personCard).perform()
        name = container_personCard.find_element(By.XPATH, ".//h4[@data-component='PersonCardFullName']")
        name = name.get_attribute('innerHTML')
        personal_link = container_personCard.find_element(By.XPATH,".//a[@data-component = 'PersonCardBoxLink']").get_attribute(
            'href')

        with open('result_1.csv', 'a', encoding='utf-8', newline='') as files:
            writer = csv.writer(files, delimiter=';')
            writer.writerow([x for x in [state, residence, name, personal_link]])

        try:
            container_personCard = container_personCard.find_element(By.XPATH,
                                                                     "following-sibling::div[@class='Box-sc-ucqo0b-0 vDyOp']")
        except:
            break


async def get_data(state, residence, link):
        """scroll cards (function scroll_cards),
        pagination"""

        with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=options_chrome) as driver:
                driver.get(link)

                counter = 1
                while True:
                    if counter == 1:
                        scroll_cards(driver, state, residence)
                        counter += 1
                    else:
                        ActionChains(driver).scroll_by_amount(delta_x=0, delta_y=500).perform()
                        try:
                            pagen = driver.find_element(By.XPATH,
                                                        f"//div[@data-component='PaginationNavigationContainer']/button[contains(.,'{counter}')]")

                            pagen.click()
                            scroll_cards(driver, state, residence)
                            counter += 1
                        except:
                            break


async def get_details(link):
    """gets additional data (description) from each personal page
            link from the existing file, which I filled earlier,
            gets data from description with regular expressions"""

    with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=options_chrome) as driver:
            driver.get(link)
            # find description
            description = driver.find_element(By.XPATH, "//div[@data-component = 'ObituaryParagraph']").text.lower()
            try:
                age = re.findall(r".*age.*? ([0-9]+)", description.lower())
                DOD = re.findall(r".*passed away .*?on.*? ([a-z]+\s+\d\d,\s+\d\d\d\d)", description.lower())
                wife = re.findall(r'(?<=his wife. )[a-z]+\s+[a-z]+', description.lower())
                husband = re.findall(r'(?<=her husband. )[a-z]+\s+[a-z]+', description.lower())
                son = re.findall(r'(?<=son. )[a-z]+\s+[a-z]+', description.lower())
                daughter = re.findall(r'(?<=daughter. )[a-z]+\s+[a-z]+', description.lower())
                brother = re.findall(r'(?<=brother. )[a-z]+\s+[a-z]+', description.lower())
                sister = re.findall(r'(?<=sister. )[a-z]+\s+[a-z]+', description.lower())

                with open('result_2.csv', 'a', encoding='utf-8', newline='') as files:
                    writer = csv.writer(files, delimiter=';')
                    writer.writerow([x for x in [age, DOD, wife, husband, son, daughter, brother, sister]])
            except:
                pass


async def main(states_names, names_of_residence, links):
        tasks = []
        for state, residence, link in zip(states_names, names_of_residence, links):
            task = asyncio.create_task(get_data(state, residence, link))
            tasks.append(task)
        await asyncio.gather(*tasks)

        tasks2 = []
        with open('result_1.csv', 'r') as file:
            reader = csv.reader(file, delimiter=";")
            for i, line in enumerate(reader):
                if i != 0 and i < 51:  #i<51 for test only
                    url = line[3]
                    task2 = asyncio.create_task(get_details(url))
                    tasks2.append(task2)
        await asyncio.gather(*tasks2)


url = 'https://www.legacy.com/us/obituaries/'
states_list, names_of_residence, links = get_links(url)
print(len(states_list), len(names_of_residence), len(links))

# Cut for a test purpose (remove for a full scan)
names_of_residence_test = names_of_residence[:1]
states_list_test = states_list[:1]
links_test = links[:1]
print(len(links_test), len(names_of_residence_test), len(states_list_test))

save_csv('result_1.csv', ['state', 'place_of_residence', 'name', 'link'])
save_csv('result_2.csv', ['age', 'Passed_away_Date', 'wife', 'husband', 'son', 'daughter', 'brother', 'sister'])

asyncio.run(main(states_list_test, names_of_residence_test, links_test))

df1 = pd.read_csv('result_1.csv', delimiter=';')
df2 = pd.read_csv('/content/result_2.csv', delimiter=';')
df2 = df2.applymap(lambda x: x.replace('[', ''))
df2 = df2.applymap(lambda x: x.replace(']', ''))
df2 = df2.applymap(lambda x: x.replace("'", ''))
df_result = df1.join(df2)
df_result.to_csv('total_data.csv')
print('----file id ready!----')
