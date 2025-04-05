import psycopg2

class DatabaseManager:
    def __init__(self, database, host, user, password, port):
        self.database = database
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establishes connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                database=self.database,
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            print("Database connection established.")
            return self.conn
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to database: {error}")
            return None

    def close(self):
        """Closes the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")

    def create_tables(self):
        """Creates necessary tables in the database."""
        commands = (
            """ CREATE TABLE IF NOT EXISTS SECTOR (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE
                )
            """,
            """ CREATE TABLE IF NOT EXISTS COMPANIES (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE,
                    sector_id INT REFERENCES SECTOR(id) ON DELETE CASCADE,
                    symbol TEXT UNIQUE,
                    listed_shares NUMERIC(16, 2),
                    market_cap NUMERIC(16, 2),
                    paid_up_capital NUMERIC(16, 2)
                )
            """,
            """ CREATE TABLE IF NOT EXISTS REPORTS (
                    id SERIAL PRIMARY KEY,
                    company_id INT REFERENCES COMPANIES(id) ON DELETE CASCADE,
                    report_type TEXT CHECK (report_type IN ('Balance Sheet', 'Profit & Loss', 'Key Metrics', 'Ratio Analysis', 'Others')),
                    fiscal_year TEXT,
                    quarter INT,
                    uploaded_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE (company_id, fiscal_year, quarter, report_type)
                )
            """,
            """ CREATE TABLE IF NOT EXISTS REPORT_DATA (
                    id SERIAL PRIMARY KEY,
                    report_id INT REFERENCES REPORTS(id) ON DELETE CASCADE,
                    metric TEXT,
                    value NUMERIC
                )
            """
        )
        try:
            _ = self.connect()
            for command in commands:
                self.cursor.execute(command)
            self.conn.commit()
            print("Tables created successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error creating tables: {error}")
            if self.conn:
                self.conn.rollback()
        finally:
            self.close()

# Example usage
if __name__ == "__main__":
    db_manager = DatabaseManager(database="nepse", host="localhost", user="postgres", password="1234", port="5433")
    db_manager.create_tables()
