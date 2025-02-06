from selenium import webdriver
from selenium.webdriver.common.by import By

import pandas as pd
import time 

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

driver = webdriver.Chrome()

url = 'https://www.sharesansar.com/company-list'
driver.get(url)

# For Company list
time.sleep(2)
form = driver.find_elements(By.XPATH, "//form[@id='frm_listed']")
company_list = form[0].find_elements(By.XPATH, "//select[@name='sector']/option")
company_list = [company.get_attribute('value') for company in company_list]

# select each option and extract table 
for company in company_list:
    # breakpoint()
    driver.find_element(By.XPATH, "//select[@name='sector']/option[@value='{}']".format(company)).click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[@id='btn_listed_submit']").click()
    time.sleep(2)
    table = driver.find_element(By.ID, 'myTable')
    table = table.get_attribute('outerHTML')
    df = pd.read_html(table)[0]
    df.to_csv(f"{company}.csv", index=False)

driver.quit()


'''
# For Financial report
# url = 'https://www.sharesansar.com/company/adbl#cqtrreport'
driver.get(url)

driver.find_element(By.LINK_TEXT, 'Financials').click()
driver.find_element(By.LINK_TEXT, 'Quarterly Reports').click()


quarterly_reports = driver.find_element(By.CLASS_NAME, 'myQtrReport')
time.sleep(5)
# Prepare an empty list to store DataFrames

keys = ['balance', 'profitloss', 'keymetrics']

tables = quarterly_reports.find_elements(By.TAG_NAME, 'table')
for i, table in enumerate(tables):
    table_html = table.get_attribute('outerHTML')
    df = pd.read_html(table_html)[0]
    df.to_csv(f"{keys[i]}_report.csv", index=False)

driver.quit()
'''
