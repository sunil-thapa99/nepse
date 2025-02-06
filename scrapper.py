from selenium import webdriver
from selenium.webdriver.common.by import By

import pandas as pd
import time 

url = 'https://www.sharesansar.com/company/adbl#cqtrreport'
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

driver = webdriver.Chrome()

driver.get(url)

driver.find_element(By.LINK_TEXT, 'Financials').click()
driver.find_element(By.LINK_TEXT, 'Quarterly Reports').click()


quarterly_reports = driver.find_element(By.CLASS_NAME, 'myQtrReport')
time.sleep(5)
# Prepare an empty list to store DataFrames
dfs = {
    'balance': pd.DataFrame(),
    'profitloss': pd.DataFrame(),
    'keymetrics': pd.DataFrame()
}
keys = ['balance', 'profitloss', 'keymetrics']

tables = quarterly_reports.find_elements(By.TAG_NAME, 'table')
for i, table in enumerate(tables):
    table_html = table.get_attribute('outerHTML')
    df = pd.read_html(table_html)[0]
    df.to_csv(f"{keys[i]}_report.csv", index=False)

'''
# breakpoint()
time.sleep(5)
divs = quarterly_reports.find_elements(By.TAG_NAME, 'div')

# Prepare an empty list to store DataFrames
dfs = {
    'balance': pd.DataFrame(),
    'profitloss': pd.DataFrame(),
    'keymetrics': pd.DataFrame()
}
keys = ['balance', 'profitloss', 'keymetrics']

# Loop through divs and extract each table into a DataFrame
for i, div in enumerate(divs[1:]):
    # Find the table inside each div
    table = div.find_element(By.TAG_NAME, 'table')
    # Extract the table HTML
    table_html = table.get_attribute('outerHTML')

    # Read the HTML of the table into a DataFrame
    df = pd.read_html(table_html)[0]
    print(df.head())

    if df.empty:
        print(f"DataFrame {keys[i]} is empty")
        continue
    print('\n\n\n\n\n')
    print('-----------------------------------')
    # Save the DataFrame to the dictionary with the div class name as the key
    # dfs[keys[i]] = df

# Optionally, save the DataFrames to CSV
dfs[0].to_csv("balance_report.csv", index=False)
dfs[1].to_csv("profitloss_report.csv", index=False)
dfs[2].to_csv("keymetrics_report.csv", index=False)

# time.sleep(5)
driver.quit()
'''