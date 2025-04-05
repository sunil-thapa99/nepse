# NEPSE Financial Report QA System

## Overview
This project focuses on developing a Question Answering (QA) system for NEPSE-listed companies based on their financial reports. The system utilizes LangChain, NLP models, and a vector database to enable intelligent querying of structured financial data.

## Features
- **Automated Data Extraction**: Uses Selenium to scrape and extract tabular financial data from reports.
- **Efficient Storage & Retrieval**: Stores extracted data in a vector database for optimized search and retrieval.
- **NLP-Powered QA**: Leverages Natural Language Processing (NLP) and LangChain to facilitate intelligent querying.
- **Open-Source Model Integration**: Potentially integrates with Ollama as an open-source alternative for QA.

## Tech Stack
- **Python**: Core language for implementation.
- **Selenium**: For web scraping and data extraction.
- **PostgreSQL**: Used as a database
- **LangChain**: Framework for developing LLM-powered applications.
- **Vector Database**: (e.g., FAISS, ChromaDB, Pinecone) for efficient retrieval of relevant documents.
- **Ollama (Optional)**: Open-source LLM for QA processing.
- **Hugging Face Transformers**: For NLP model integration if needed.

## Pipeline Workflow
1. **Data Extraction**
   - Use Selenium to navigate and extract tabular data from NEPSE-listed company financial reports.
   - Parse extracted data into structured format (CSV, JSON, or DataFrame).

2. **Data Storage & Indexing**
   - Convert structured data into vector representations using embeddings.
   - Store vectorized data in a vector database for fast retrieval.

3. **Question Answering using LangChain**
   - Accept user queries related to financial reports.
   - Retrieve relevant financial data using semantic search.
   - Process retrieved data with an LLM for accurate responses.

4. **Response Generation**
   - Use NLP techniques to generate precise and context-aware answers.
   - Optionally integrate Ollama for enhanced QA capabilities.

## Installation & Setup
### Prerequisites
Ensure you have the following installed:
- Python (3.10)
- pip
- ChromeDriver (for Selenium)

### Installation Steps
```bash
# Clone the repository
git clone https://github.com/sunil-thapa99/nepse.git
cd nepse

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Create database
```bash
# Navigate to database directory 
cd scrapper
python create.py
```

### Data Extraction
```bash
# Navigate to scrapper directory
cd scrapper
```
To automate the extraction of company list and it's financial data, run: 
```bash
python scrap.py
```

If you want to individually any set of codes:
-  Run the following command to extract company list:
      ```bash
      python company_scrapper.py
      ```
-  Run the following command to extract financial data:
      ```bash
      python financial_scrapper.py
      ```

#### TO-DO:
-  If companies financial report is stored in report_data, don't duplicatly store it: Financial Scrapper -> function insert_report_data
-  Remove creation of data directory

### Data Processing & Storage
```bash

```

### Question Answering
```bash

```
Then, you can interact with the QA system via an API or CLI.

## Future Enhancements
- Expand data sources to include more financial reports and formats.
- Optimize query performance using advanced retrieval techniques.
- Improve response accuracy with fine-tuned LLMs.

## License
MIT License


## Contact
For queries, please reach out to [sunil43thapa@gmail.com].

