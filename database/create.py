import psycopg2

def connect():
    conn = psycopg2.connect(database="nepse",
                            host="localhost",
                            user="postgres",
                            password="1234",
                            port="5433")
    cursor = conn.cursor()
    return cursor, conn

def create_tables():
    """ Create tables in the PostgreSQL database """
    commands = (
        """ CREATE TABLE IF NOT EXISTS SECTOR (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE,
            )
        """,
        """ CREATE TABLE IF NOT EXISTS COMPANIES (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE,
                sector_id  INT REFERENCES SECTOR(id) ON DELETE CASCADE,
                symbol TEXT UNIQUE,
                listed_shares INT,
                market_cap INT,
                paid_up_capital INT
            )
        """,
        """ CREATE TABLE IF NOT EXISTS REPORTS (
                id SERIAL PRIMARY KEY,
                company_id INT REFERENCES COMPANIES(id) ON DELETE CASCADE,
                report_type TEXT CHECK (report_type IN ('Balance Sheet', 'Profit & Loss', 'Key Metrics', 'Ratio Analysis', 'Others')),
                fiscal_year INT,
                quarter INT,
                uploaded_at TIMESTAMP DEFAULT NOW(),
                UNIQUE (company_id, fiscal_year, quarter, report_type)
            )
        """,
        """ CREATE TABLE IF NOT EXISTS REPORT_DATA (
                id SERIAL PRIMARY KEY,
                report_id INT REFERENCES REPORTS(id) ON DELETE CASCADE,
                metric TEXT,  -- Column name from CSV (e.g., 'Total Assets', 'Net Profit')
                value NUMERIC  -- The actual numerical value of the metric
            )
        """
    )
    try:
        cursor, conn = connect()
        # Execute each command in a transaction
        for command in commands:
            cursor.execute(command)

        # Commit changes
        conn.commit()
        print("Tables created successfully.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn:
            conn.rollback()  # Rollback on error
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
