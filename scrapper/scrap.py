from company_scrapper import CompanyListScraper
# # from financial_scrapper import FinancialReportScraper
import os
import sys
# import pandas as pd

def main():
    
    try:
        # Step 1: Scrape the list of companies
        
        print("Starting Company List Scraper...")
        company_scraper = CompanyListScraper()
        company_scraper.run()
        print("Company list scraping completed.")
        
        '''
        # Read the extracted company list
        keywords = ["debentures", "bonds", "mutual", "preference", "promoter"]
        company_files = [
            os.path.join(company_list_dir, f)
            for f in os.listdir(company_list_dir)
            if f.endswith(".csv") and all(keyword not in f.lower() for keyword in keywords)
        ]
        # company_files = [os.path.join(company_list_dir, f) for f in os.listdir(company_list_dir) if f.endswith(".csv")]
        
        for company_file in company_files:
            df = pd.read_csv(company_file)
            company_names = df['Symbol'].tolist()
            
            # Step 2: Scrape financial reports for each company
            for company in company_names:
                print(f"Starting Financial Report Scraper for {company}...")
                company_url = f"https://www.sharesansar.com/company/{company}"
                company_report_dir = os.path.join(financial_reports_dir, company) 
                report_scraper = FinancialReportScraper(url=company_url, output_dir=company_report_dir)
                report_scraper.run()
                report_scraper.close()
                print(f"Financial report scraping completed for {company}.")
        print("All scraping processes completed successfully.")
        '''
    except Exception as e:
        print(f"Error during scraping process: {e}")

if __name__ == "__main__":
    main()
