import sqlite3 as sq3

class DB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection, self.cursor = self.connect_to_db(db_path)

    # connects to database
    # returns connection, cursor
    def connect_to_db(self, path):
        connection = sq3.connect(path)
        cursor = connection.cursor()
        return connection, cursor

    # pass sql file, will execute queries in file
    # accepted sql format:
    # newline between query
    def execute_queries_from_file(self, sql_file_path):
        if sql_file_path[-4:] != ".sql":
            sql_file_path += ".sql"
        with open(sql_file_path, "r") as sql_file_path:
            query = ""
            for char in sql_file_path.read():
                query += char
                if char == ";":
                    self.cursor.execute(query)
                    query = ""
            self.connection.commit()

    def close_connection(self):
        self.connection.close()

    def display_all_records(self, table_name):
        query = "SELECT * FROM {0}".format(table_name)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

if __name__ == "__main__":
    db = DB("Blackjack.sqlite")
    #db.execute_queries_from_file("Create_Agents_Table")
    #db.execute_queries_from_file("Populate_Agents")
    db.display_all_records("Agents")
    db.close_connection()