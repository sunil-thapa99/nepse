from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

import time
import os
import sys
import warnings
warnings.filterwarnings("ignore")

from financial_scrapper import FinancialReportScraper

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
# Define output directories
company_list_dir = os.path.join(ROOT_DIR, "data/company_list")
financial_reports_dir = os.path.join(ROOT_DIR, "data/financial_reports")

# Ensure directories exist
if not os.path.exists(company_list_dir):
    os.makedirs(company_list_dir)
if not os.path.exists(financial_reports_dir):
    os.makedirs(financial_reports_dir)

# Database connection
from database.create import DatabaseManager

class CompanyListScraper:
    def __init__(self, url='https://www.sharesansar.com/company-list', output_dir='.',): 
        """
        Initializes the scraper with the target URL and output directory.
        Establishes a database connection and initializes the web driver.
        """
        self.url = url
        self.output_dir = output_dir
        self.db_manager = DatabaseManager(database="nepse", host="localhost", user="postgres", password="1234", port="5433")
        self.db_manager.create_tables()
        self.conn = self.db_manager.connect()
        self.cursor = self.conn.cursor()
        try:
            self.driver = webdriver.Chrome()
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            raise
    
    def open_page(self):
        """Opens the target webpage using Selenium."""
        try:
            self.driver.get(self.url)
            time.sleep(2)
        except Exception as e:
            print(f"Error opening page: {e}")
    
    def get_company_list(self):
        """
        Extracts the list of available sectors from the dropdown menu.
        Returns a list of sector values.
        """
        try:
            form = self.driver.find_elements(By.XPATH, "//form[@id='frm_listed']")
            company_list = form[0].find_elements(By.XPATH, "//select[@name='sector']/option")
            return [company.get_attribute('value') for company in company_list]
        except Exception as e:
            print(f"Error retrieving company list: {e}")
            return []

    def insert_sector(self, sector_name):
        """
        Inserts a sector into the SECTOR table if it does not already exist.
        Returns the sector ID.
        """
        try:
            self.cursor.execute("INSERT INTO SECTOR (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (sector_name,))
            sector_id = self.cursor.fetchone()
            if sector_id is None:
                self.cursor.execute("SELECT id FROM SECTOR WHERE name = %s", (sector_name,))
                sector_id = self.cursor.fetchone()[0]
            else:
                sector_id = sector_id[0]
            self.conn.commit()
            return sector_id
        except Exception as e:
            print(f"Error inserting sector {sector_name}: {e}")
            return None
    
    def insert_or_update_company(self, name, symbol, sector_id, listed_shares, paid_up_capital, market_cap):
        """
        Inserts a new company into the COMPANIES table or updates it if it already exists.
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO COMPANIES (name, symbol, sector_id, listed_shares, paid_up_capital, market_cap) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                ON CONFLICT (name) 
                DO UPDATE SET symbol = EXCLUDED.symbol, 
                              sector_id = EXCLUDED.sector_id, 
                              listed_shares = EXCLUDED.listed_shares, 
                              paid_up_capital = EXCLUDED.paid_up_capital,
                              market_cap = EXCLUDED.market_cap
                """,
                (name, symbol, sector_id, listed_shares, paid_up_capital, market_cap)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting/updating company {name}: {e}")
    
    def extract_company_data(self, company):
        """
        Extracts company data for a specific sector, inserts the data into the database,
        and saves it to a CSV file.
        """
        try:
            option = self.driver.find_element(By.XPATH, f"//select[@name='sector']/option[@value='{company}']")
            option.click()
            select_text = option.text
            time.sleep(2)
            sector_id = self.insert_sector(select_text)
            
            self.driver.find_element(By.XPATH, "//button[@id='btn_listed_submit']").click()
            time.sleep(2)
            all_data = []
            while True:
                try:
                    table = self.driver.find_element(By.ID, 'myTable')
                    table_html = table.get_attribute('outerHTML')
                    df = pd.read_html(table_html)[0]
                    all_data.append(df)
                    next_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Next')]")
                    if "disabled" in next_button.get_attribute("class"):
                        break
                    else:
                        next_button.click()
                        time.sleep(2)
                except Exception as e:
                    print(f"Error navigating pagination: {e}")
                    break
            combined_df = pd.concat(all_data, ignore_index=True)
            # combined_df.columns = ['S.N.', 'Symbol', 'Company', 'Listed Shares', 'Paid-up (Rs)', 'Total Paid-up Capital (Rs)', 'Market Capitalization (Rs)', 'Date of Operation', 'LTP', 'As Of']

            for _, row in combined_df.iterrows():
                print(sector_id, row['Company'])
                self.insert_or_update_company(
                    row['Company'], row['Symbol'], sector_id, 
                    row['Listed Share'], row['Total Paid-up Capital (Rs)'], row['Market Capitalization (Rs)']
                )
            
            company_csv_path = f"{self.output_dir}/{select_text}.csv"
            combined_df.to_csv(company_csv_path, mode='w', index=False)
            print(f"Data for {select_text} has been saved.")
        except Exception as e:
            print(f"Error extracting data for {company}: {e}")
    
    def fetch_financial_reports(self):
        """
        Fetches financial reports for a specific company.
        """
        self.cursor.execute("SELECT id, symbol FROM COMPANIES")
        companies = self.cursor.fetchall()

        # Scrape financial reports for each company
        for company_id, symbol in companies:
            print(f"Processing financial reports for {symbol}...")
            try:
                company_url = f"https://www.sharesansar.com/company/{symbol.lower()}"
                company_report_dir = os.path.join(financial_reports_dir, symbol.lower()) 
                report_scraper = FinancialReportScraper(company_id=company_id, url=company_url, 
                                                        output_dir=company_report_dir, conn=self.conn)
                report_scraper.run()
                break
            except Exception as e:
                print(f"Failed to extract information for: {symbol}: {e}")
        self.close()

    def close(self):
        """Closes the Selenium WebDriver and the database connection."""
        self.driver.quit()
        self.cursor.close()
        self.conn.close()
    
    def run(self):
        """
        Executes the full scraping process by opening the webpage, extracting companies,
        inserting/updating records, and saving data to CSV files.
        """
        try:
            self.open_page()
            company_list = self.get_company_list()
            for company in company_list:
                self.extract_company_data(company)
                break
            self.fetch_financial_reports()
        except Exception as e:
            print(f"Unexpected error in run method: {e}")
            self.close()

if __name__ == "__main__":
    try:
        scraper = CompanyListScraper(output_dir='../data/company_list')
        scraper.run()
    except Exception as e:
        print(f"Fatal error in main execution: {e}")
