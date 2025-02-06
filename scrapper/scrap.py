from scrapper.financial_scrapper import FinancialReportScraper

# Scrap company list from Sharesansar
url = 'https://www.sharesansar.com/company-list'

scraper = FinancialReportScraper(url, find_by=By.LINK_TEXT, tab_list=['Financials', 'Quarterly Reports'])
scraper.open_page()
scraper.navigate_to_reports()
scraper.extract_tables()
