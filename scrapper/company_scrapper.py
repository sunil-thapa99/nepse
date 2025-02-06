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
        self.driver = webdriver.Chrome()  # Initializes the Selenium WebDriver for Chrome
    
    def open_page(self):
        """Opens the target webpage using Selenium."""
        self.driver.get(self.url)
        time.sleep(2)  # Wait for page to load
    
    def get_company_list(self):
        """Extracts the list of available sectors from the dropdown menu."""
        form = self.driver.find_elements(By.XPATH, "//form[@id='frm_listed']")
        company_list = form[0].find_elements(By.XPATH, "//select[@name='sector']/option")
        return [company.get_attribute('value') for company in company_list]

    def extract_company_data(self, company):
        """
        Selects a company sector, extracts the table data, and saves it as a CSV file.
        This method also handles pagination, extracting data from multiple pages if needed.
        If the data is already extracted (based on content), it does not save again.

        Parameters:
        - company (str): The value attribute of the company sector option.
        """

        option = self.driver.find_element(By.XPATH, f"//select[@name='sector']/option[@value='{company}']")
        option.click()
        select_text = option.text
        time.sleep(2)
        company_csv_path = f"{self.output_dir}/{select_text}.csv"
        
        self.driver.find_element(By.XPATH, "//button[@id='btn_listed_submit']").click()
        time.sleep(2)
        all_data = []  # To store all pages' data

        while True:
            # Extract table data
            table = self.driver.find_element(By.ID, 'myTable')
            table_html = table.get_attribute('outerHTML')
            df = pd.read_html(table_html)[0]
            all_data.append(df)

            # Check for the "Next" button (adjust the XPath based on the actual button on the site)
            try:
                next_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Next')]")
                if "disabled" in next_button.get_attribute("class"):  # Checks if "Next" button is disabled
                    break  # Exit loop if "Next" is disabled
                else:
                    next_button.click()  # Go to the next page
                    time.sleep(2)  # Wait for the next page to load
            except:
                break  # No "Next" button found, so exit loop

        # Combine all data and save as CSV
        combined_df = pd.concat(all_data, ignore_index=True)

        # Skip saving if the same data already exists in the CSV
        if os.path.exists(company_csv_path):
            existing_df = pd.read_csv(company_csv_path)
            
            # Compare the current extracted data with the existing data
            if combined_df.equals(existing_df):
                print(f"Data for {select_text} is already up-to-date, skipping...")
                return  # Skip saving if the data is the same

        # Save the extracted data to CSV if it's new
        combined_df.to_csv(company_csv_path, mode='w', index=False)
        print(f"Data for {select_text} has been saved.")
    
    def close(self):
        """Closes the Selenium WebDriver."""
        self.driver.quit()
    
    def run(self):
        """Executes the full scraping process."""
        self.open_page()
        company_list = self.get_company_list()
        for company in company_list:
            self.extract_company_data(company)
            break
        self.close()

if __name__ == "__main__":
    scraper = CompanyListScraper(output_dir='../data/company_list')
    scraper.run()