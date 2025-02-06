from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
import warnings
warnings.filterwarnings("ignore")

class FinancialReportScraper:
    def __init__(self, url, find_by=By.LINK_TEXT, tab_list=['Financials', 'Quarterly Reports'], 
                 table_parent_div='myQtrReport', keys=['balance', 'profitloss', 'keymetrics'],
                 output_dir='.'):
        self.url = url
        self.find_by = find_by
        self.tab_list = tab_list
        self.table_parent_div = table_parent_div
        self.keys = keys
        self.output_dir = output_dir
        self.driver = webdriver.Chrome()
        self.reports = {}
    
    def open_page(self):
        self.driver.get(self.url)
    
    def navigate_to_reports(self):
        for tab in self.tab_list:
            self.driver.find_element(self.find_by, tab).click()
            time.sleep(5)  # Allow time for page to load

    def extract_tables(self):
        quarterly_reports = self.driver.find_element(By.CLASS_NAME, self.table_parent_div)
        tables = quarterly_reports.find_elements(By.TAG_NAME, 'table')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        for i, table in enumerate(tables):
            table_html = table.get_attribute('outerHTML')
            df = pd.read_html(table_html)[0]
            if df is not None:
                df.to_csv(os.path.join(self.output_dir, f"{self.keys[i]}_report.csv"), index=False)
    
    def close(self):
        self.driver.quit()
        
    
    def run(self):
        self.open_page()
        self.navigate_to_reports()
        self.extract_tables()
        self.close()

if __name__ == "__main__":
    scraper = FinancialReportScraper(
        url='https://www.sharesansar.com/company/adbl',
        output_dir='../data/adbl'
        )
    scraper.run()
