from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
import warnings

# Suppress warnings to keep the output clean
warnings.filterwarnings("ignore")

class FinancialReportScraper:
    """
    A web scraper to extract financial reports from a given company's page on Sharesansar.
    The scraper navigates through financial report tabs and extracts tables into CSV files.
    """

    def __init__(self, url, find_by=By.LINK_TEXT, tab_list=['Financials', 'Quarterly Reports'], 
                 table_parent_div='myQtrReport', keys=['balance', 'profitloss', 'keymetrics'],
                 output_dir='.'):
        """
        Initializes the scraper with the necessary parameters.

        Parameters:
        - url (str): The target webpage URL.
        - find_by (selenium.webdriver.common.by.By): The method to locate elements (default: By.LINK_TEXT).
        - tab_list (list): List of tab names to navigate through.
        - table_parent_div (str): Class name of the parent div containing financial tables.
        - keys (list): List of table identifiers to use as filenames.
        - output_dir (str): Directory to store the extracted CSV files.
        """
        self.url = url
        self.find_by = find_by
        self.tab_list = tab_list
        self.table_parent_div = table_parent_div
        self.keys = keys
        self.output_dir = output_dir
        try:
            self.driver = webdriver.Chrome()  # Initializes the Selenium WebDriver for Chrome
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            raise
        self.reports = {}  # Dictionary to store extracted report data

    def open_page(self):
        """Opens the target webpage using Selenium."""
        try:
            self.driver.get(self.url)
        except Exception as e:
            print(f"Error opening page: {e}")

    def navigate_to_reports_tab(self):
        """Navigates through the specified financial report tabs."""
        try:
            for tab in self.tab_list:
                self.driver.find_element(self.find_by, tab).click()  # Clicks on the tab
                time.sleep(5)  # Waits for the page to load
        except Exception as e:
            print(f"Error navigating to reports tab: {e}")

    def extract_tables(self):
        """Extracts financial data tables and saves them as CSV files."""
        try:
            quarterly_reports = self.driver.find_element(By.CLASS_NAME, self.table_parent_div)  # Finds the parent div
            tables = quarterly_reports.find_elements(By.TAG_NAME, 'table')  # Finds all table elements inside the div
            if len(tables) == 4:
                self.keys = ['balance', 'profitloss', 'ratioanalysis', 'keymetrics']
            elif len(tables) == 5:
                self.keys = ['balance', 'profitloss', 'ratioanalysis', 'keymetrics', 'others']
            else:
                self.keys = ['balance', 'profitloss', 'keymetrics']
            # Ensure the output directory exists
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            # Iterate through tables and save them as CSV files
            for i, table in enumerate(tables):
                table_html = table.get_attribute('outerHTML')  # Extracts table HTML
                df = pd.read_html(table_html)[0]  # Converts HTML table to DataFrame
                if df is not None:
                    df.to_csv(os.path.join(self.output_dir, f"{self.keys[i]}_report.csv"), index=False)
        except Exception as e:
            print(f"Error extracting tables: {e}")
            raise

    def close(self):
        """Closes the Selenium WebDriver."""
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Error closing WebDriver: {e}")

    def run(self):
        """Executes the full scraping process."""
        try:
            self.open_page()
            self.navigate_to_reports_tab()
            self.extract_tables()
        except Exception as e:
            print(f"Unexpected error in run method: {e}")
        # finally:
        #     self.close()

if __name__ == "__main__":
    try:
        # Instantiate and run the scraper for ADBL (Agricultural Development Bank Limited) financial reports
        scraper = FinancialReportScraper(
            url='https://www.sharesansar.com/company/shivm',
            output_dir='../data/financial_reports/shivm'  # Output directory for extracted CSV files
        )
        scraper.run()
        scraper.close()
    except Exception as e:
        print(f"Fatal error in main execution: {e}")