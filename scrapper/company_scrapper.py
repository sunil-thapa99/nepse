from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
import warnings
warnings.filterwarnings("ignore")

class CompanyListScraper:
    """
    A web scraper to extract company data from the Sharesansar company list page.
    It selects each sector, extracts company data, and saves it as CSV files.
    """
    
    def __init__(self, url='https://www.sharesansar.com/company-list', output_dir='.'):
        """
        Initializes the scraper with the target URL and output directory.

        Parameters:
        - url (str): The URL of the company list page.
        - output_dir (str): Directory where extracted CSV files will be stored.
        """
        self.url = url
        self.output_dir = output_dir
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
        """Extracts the list of available sectors from the dropdown menu."""
        try:
            form = self.driver.find_elements(By.XPATH, "//form[@id='frm_listed']")
            company_list = form[0].find_elements(By.XPATH, "//select[@name='sector']/option")
            return [company.get_attribute('value') for company in company_list]
        except Exception as e:
            print(f"Error retrieving company list: {e}")
            return []

    def extract_company_data(self, company):
        """
        Selects a company sector, extracts the table data, and saves it as a CSV file.
        This method also handles pagination, extracting data from multiple pages if needed.
        If the data is already extracted (based on content), it does not save again.

        Parameters:
        - company (str): The value attribute of the company sector option.
        """

        try:
            option = self.driver.find_element(By.XPATH, f"//select[@name='sector']/option[@value='{company}']")
            option.click()
            select_text = option.text
            time.sleep(2)
            company_csv_path = f"{self.output_dir}/{select_text}.csv"
            
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

            if os.path.exists(company_csv_path):
                existing_df = pd.read_csv(company_csv_path)
                if combined_df.equals(existing_df):
                    print(f"Data for {select_text} is already up-to-date, skipping...")
                    return

            combined_df.to_csv(company_csv_path, mode='w', index=False)
            print(f"Data for {select_text} has been saved.")
        except Exception as e:
            print(f"Error extracting data for {company}: {e}")
    
    def close(self):
        """Closes the Selenium WebDriver."""
        self.driver.quit()
    
    def run(self):
        """Executes the full scraping process."""
        try:
            self.open_page()
            company_list = self.get_company_list()
            for company in company_list:
                self.extract_company_data(company)
            self.close()
        except Exception as e:
            print(f"Unexpected error in run method: {e}")
            self.close()

if __name__ == "__main__":
    try:
        scraper = CompanyListScraper(output_dir='../data/company_list')
        scraper.run()
    except Exception as e:
        print(f"Fatal error in main execution: {e}")