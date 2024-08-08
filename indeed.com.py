from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import re
import time
import csv
from selenium.webdriver import ActionChains
import asyncio
from selenium.webdriver.support import expected_conditions as EC

options_chrome = webdriver.ChromeOptions()
# options_chrome.add_argument('--headless')
options_chrome.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36")
options_chrome.add_argument("Content-Type=text/html; charset=utf-8")
# headers = {
#
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#         'Connection': 'keep-alive',
#         'Content-Type': 'text/html; charset=utf-8',
#
#     }

def save_csv(name_of_file, fields):
    """creates empty csv file with header fields"""
    with open(name_of_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(fields)

save_csv('indeed_data.csv', ['vacancy_name', 'link', 'company_name', 'company_rating', 'salary', 'requirements', 'responsibilities', 'qualifications', 'skills', 'clearance'])

url = 'https://www.indeed.com/'
with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=options_chrome) as driver:
    driver.get(url)
    # driver.find_element(By.XPATH, '//input[@id="text-input-where"]').clear()
    # driver.find_element(By.XPATH, '//input[@id="text-input-where"]').send_keys('United States')
    # driver.find_element(By.XPATH, '//button[@type="submit"]').click()

    driver.find_element(By.XPATH, "//input[@id='text-input-what']").send_keys('Data Engineer')
    # driver.find_element(By.XPATH, "//button[@aria-label='Clear location input']").click()
    driver.find_element(By.XPATH, '//input[@id="text-input-where"]').clear()
    # driver.find_element(By.XPATH, '//input[@id="text-input-where"]').send_keys('United States')
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()


    # all possible filters
    # filters = driver.find_elements(By.XPATH, "//ul[@class='yosegi-FilterPill-pillList css-zhqt0z eu4oa1w0']/li")
    # values = []
    # for filter in filters:
    #     dropdownList = filter.find_elements(By.XPATH, ".//ul[@class='yosegi-FilterPill-dropdownList']/li/a")
    #     values = [value.get_attribute('innerHTML') for value in dropdownList]
        # print(values)
    # all possible filters

    # filter = posted last 24 hours
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[@id ='filter-dateposted']").click()
    driver.find_element(By.XPATH, "//ul[@id='filter-dateposted-menu']/li[1]").click()

    # filter = remote
    try:
        time.sleep(2)
        driver.find_element(By.XPATH, "//button[@id='filter-remotejob']").click()
        driver.find_element(By.XPATH, "//ul[@id='filter-remotejob-menu']/li[1]").click()
    except:
        "No remote vacancies"

    # WebDriverWait(driver,10).until(EC.element_to_be_clickable(btn_date)).click()
    time.sleep(20)

    # pagination
    counter = 1
    while True:
        if counter != 1:
            try:
                pagen = driver.find_element(By.XPATH, f"//nav[@role='navigation']/ul/li[{counter}]")
                pagen.click()
                counter += 1
            except:
                break
        else:
            counter += 1

        # look for vacancies
        try:
            vacancycard = driver.find_element(By.XPATH, "//ul[@class='css-zu9cdh eu4oa1w0']/li[1]")
        except:
            print('No new vacancies')

        while True:
                # ActionChains(driver).scroll_to_element(vacancycard).perform()
                driver.execute_script("return arguments[0].scrollIntoView(true);", vacancycard)

                time.sleep(2)

                try:
                    vacancy_name = vacancycard.find_element(By.XPATH, ".//h2[@class='jobTitle css-198pbd eu4oa1w0']").text
                    print(vacancy_name)
                except:
                    # it is not a vacancy card
                    try:
                        vacancycard = vacancycard.find_element(By.XPATH, "following-sibling::li[@class='css-5lfssm eu4oa1w0']")
                        continue
                    except:
                        break

                # vacancy_link
                vacancy_link = vacancycard.find_element(By.XPATH, "//a").get_attribute('href')

                # click on the link-name of the vacancy
                vacancycard.find_element(By.XPATH, ".//h2[@class='jobTitle css-198pbd eu4oa1w0']/a").click()
                time.sleep(5)
                # company name
                company_name = driver.find_element(By.XPATH, "//div[@data-testid='inlineHeader-companyName']").text
                print(company_name)

                # company rating
                company = driver.find_element(By.XPATH, "//div[@data-testid='inlineHeader-companyName']")
                try:
                    company_rating = company.find_element(By.XPATH, "following-sibling::div/span[2]").text.split(' ')[0]
                    print(company_rating)
                except:
                    company_rating = 'Unknown'

                # salary
                try:
                    salary = driver.find_element(By.XPATH, "//div[@id='salaryInfoAndJobType']/span").text
                    print(salary)
                except:
                    salary = 'Unknown'

                # benefits
                try:
                    driver.find_element(By.XPATH, "//button[@data-testid='collapsedBenefitsButton']").click()
                    benefits = driver.find_elements(By.XPATH, "//div[@id='benefits']/ul/li")
                    benefits = [b.text for b in benefits]
                    print(benefits)
                except:
                    benefits = ''

                # requirements
                try:
                    title_req = driver.find_element(By.XPATH, "//*[contains(text(),'Requirements')]/parent::p")
                    requirements = title_req.find_elements(By.XPATH, "following-sibling::ul/li")
                    requirements = [r.text for r in requirements]
                    print(requirements)
                except:
                    requirements = ''

                # skills
                try:
                    title_req = driver.find_element(By.XPATH, "//*[contains(text(),'Skills')]/parent::p")
                    skills = title_req.find_elements(By.XPATH, "following-sibling::ul/li")
                    skills = [r.text for r in skills]
                    print(skills)
                except:
                    skills = ''

                # qualifications
                try:
                    title_req = driver.find_element(By.XPATH, "//*[contains(text(),'Qualifications')]/parent::p")
                    qualifications = title_req.find_elements(By.XPATH, "following-sibling::ul/li")
                    qualifications = [r.text for r in qualifications]
                    print(qualifications)
                except:
                    qualifications = ''


                # responsibilities
                try:
                    title_req = driver.find_element(By.XPATH, "//*[contains(text(),'Responsibilities')]/parent::p")
                    responsibilities = title_req.find_elements(By.XPATH, "following-sibling::ul/li")
                    responsibilities = [r.text for r in responsibilities]
                    print(responsibilities)
                except:
                    responsibilities = ''

                # Clearance
                try:
                    clearance = driver.find_element(By.XPATH, "//*[contains(text(), 'Clearance')]").text
                    print(clearance)
                except:
                    clearance = ''

                # # job description
                # try:
                #     description = driver.find_element(By.XPATH, "//div[@id='jobDescriptionText']").get_attribute('innerHTML')
                #     print(description)
                # except:
                #     description = ''

                with open('indeed_data.csv', 'a', encoding='utf-8', newline='') as files:
                    writer = csv.writer(files, delimiter=';')
                    writer.writerow([x for x in [vacancy_name, vacancy_link, company_name, company_rating, salary, requirements, responsibilities, qualifications, skills, clearance]])

                try:
                    vacancycard = vacancycard.find_element(By.XPATH, "following-sibling::li[@class='css-5lfssm eu4oa1w0']")
                except:
                    break
