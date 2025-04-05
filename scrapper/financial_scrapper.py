from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
import warnings
import re
import sys

# Suppress warnings to keep the output clean
warnings.filterwarnings("ignore")

class FinancialReportScraper:
    """
    A web scraper to extract financial reports from a given company's page on Sharesansar.
    The scraper navigates through financial report tabs and extracts tables into CSV files.
    """
    report_type_mapping = {
        'balance': 'Balance Sheet',
        'profitloss': 'Profit & Loss',
        'ratioanalysis': 'Ratio Analysis',
        'keymetrics': 'Key Metrics',
        'others': 'Others'
    }

    def __init__(self, company_id, url, find_by=By.LINK_TEXT, tab_list=['Financials', 'Quarterly Reports'], 
                 table_parent_div='myQtrReport', keys=['balance', 'profitloss', 'keymetrics'],
                 output_dir='.', conn=None):
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
        self.company_id = company_id
        self.url = url
        self.find_by = find_by
        self.tab_list = tab_list
        self.table_parent_div = table_parent_div
        self.keys = keys
        self.output_dir = output_dir
        self.conn = conn
        self.cursor = self.conn.cursor()
        
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

    def parse_fiscal_period(self, header):
        """
        Extracts quarter and fiscal year from strings like '2nd Quarter 2081/2082'
        
        Returns:
            dict with 'quarter', 'fiscal_year'
        """
        match = re.search(r'(\d+)[a-z]{2}\s+Quarter\s+(\d{4})/(\d{4})', header, re.IGNORECASE)
        if match:
            return int(match.group(1)), f"{match.group(2)}/{match.group(3)}"
        return None, None
    
    def insert_report(self, report_type, fiscal_year, quarter):
        """Insert or get existing report record"""
        self.cursor.execute("""
            INSERT INTO REPORTS (company_id, report_type, fiscal_year, quarter)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (company_id, fiscal_year, quarter, report_type) DO NOTHING
            RETURNING id
        """, (self.company_id, report_type, fiscal_year, quarter))
        
        report_id = self.cursor.fetchone()
        if report_id:
            return report_id[0]
        
        # Get existing if conflict
        self.cursor.execute("""
            SELECT id FROM REPORTS
            WHERE company_id = %s AND report_type = %s
            AND fiscal_year = %s AND quarter = %s
        """, (self.company_id, report_type, fiscal_year, quarter))
        return self.cursor.fetchone()[0]

    def insert_report_data(self, report_id, metric, value):
        """Insert metric data for a report"""
        try:
            value = float(str(value).replace(',', '')) if value else None
            if value:
                self.cursor.execute("""
                    INSERT INTO REPORT_DATA (report_id, metric, value)
                    VALUES (%s, %s, %s)
                """, (report_id, metric.strip(), value))
        except ValueError:
            pass


    def process_table(self, table_html, report_type_key):
        """Process HTML table and store data in database"""
        df = pd.read_html(table_html)[0]
        report_type = self.report_type_mapping.get(report_type_key)
        
        # Clean column headers
        df.columns = [str(col).split('.')[0] for col in df.columns]
        print(f"Processing {report_type} report with columns: {df.columns.tolist()}")
        for col in df.columns[1:]:  # Skip metric column
            quarter, fiscal_year = self.parse_fiscal_period(col)
            print(f"Processing {report_type} for {quarter} {fiscal_year}")
            if not quarter or not fiscal_year:
                continue

            report_id = self.insert_report(report_type, fiscal_year, quarter)
            
            for _, row in df.iterrows():
                metric = row[df.columns[0]]
                value = row[col]
                self.insert_report_data(report_id, metric, value)

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
                self.process_table(table_html, self.keys[i])  # Process the table
                # df = pd.read_html(table_html)[0]  # Converts HTML table to DataFrame
                # if df is not None:
                #     df.to_csv(os.path.join(self.output_dir, f"{self.keys[i]}_report.csv"), index=False)
            self.conn.commit()
        except Exception as e:
            print(f"Error extracting tables: {e}")
            self.conn.rollback()
            raise

    def close(self):
        """Closes the Selenium WebDriver."""
        try:
            self.driver.quit()
            self.cursor.close()
            self.conn.close()
            super().close()
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
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(SCRIPT_DIR)

    sys.path.append(ROOT_DIR)
    # print(ROOT_DIR, os.getcwd())
    # exit()

    # Database connection
    from database.create import DatabaseManager
    db_manager = DatabaseManager(database="nepse", host="localhost", user="postgres", password="1234", port="5433")
    conn = db_manager.connect()
    cursor = conn.cursor()
    try:
        # Instantiate and run the scraper for ADBL (Agricultural Development Bank Limited) financial reports
        scraper = FinancialReportScraper(
            url='https://www.sharesansar.com/company/shivm',
            output_dir='../data/financial_reports/shivm',  # Output directory for extracted CSV files
            conn=conn,
            company_id=7,  # Replace with actual company ID

        )
        scraper.run()
        scraper.close()
    except Exception as e:
        print(f"Fatal error in main execution: {e}")