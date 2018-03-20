import sqlite3 as sq3
import os, sys
sys.path.append(os.path.realpath(".."))

class DB_Wrapper:
    def __init__(self, db_path):
        self.db_path = "DB/"+ db_path

    # connects to database
    # returns connection, cursor
    def connect_to_db(self, path=None):
        if path is None:
            path = self.db_path
        connection = sq3.connect(path)
        cursor = connection.cursor()
        return connection, cursor

    # pass sql file, will execute queries in file
    # accepted sql format:
    # newline between query
    def execute_queries_from_file(self, sql_file_path):
        # append file extension if not already included - defensive programming
        if sql_file_path[-4:] != ".sql":
            sql_file_path += ".sql"
        # open sql file, read and execute queries
        queries = self.read_queries_from_file(sql_file_path)
        self.execute_queries(queries)

    # opens file path, returns list of ;-separated queries
    # TODO add some query sanitation?
    def read_queries_from_file(self, sql_file_path):
        queries = []
        with open(sql_file_path, "r") as sql_file_path:
            query = ""
            for char in sql_file_path.read():
                query += char
                if char == ";":
                    queries.append(query)
                    query = ""
        return queries

    # returns true if query is safe
    def sanitize_query(self, query):
        if "drop" in query:
            return False
        else:
            return True

    # execute passed query or passed array of queries
    # keep open determines if connection remains open, if so, returns connection and cursor
    # change this so that it works with multiple open queries
    def execute_queries(self, queries, keep_open=False):
        # turns single query into executable form - defensive programming
        if isinstance(queries, str):
            queries = [queries]
        connection, cursor = self.connect_to_db()  # open connection
        for index, query in enumerate(queries):
            # if parameter does not exist, just execute query
            try:
                print(query)
                cursor.execute(query)
            except Exception as e:
                print(e)
                return e
            connection.commit()
        if keep_open:
            return connection, cursor
        else:
            connection.close()
            return True

    def display_all_records(self, table_name):
        connection, cursor = self.connect_to_db(self.db_path)  # open connection
        query = "SELECT * FROM " + table_name
        cursor.execute(query)
        rows = cursor.fetchall()
        connection.close()
        for row in rows:
            print(row)

if __name__ == "__main__":
    db = DB("Blackjack.sqlite")
    db.execute_queries_from_file("Create_Agents_Table")
    db.execute_queries_from_file("Populate_Agents")
    db.execute_queries_from_file("Create_Games_Record")
    db.execute_queries('INSERT INTO "Game_Record" (winner_id, winning_hand, winning_hand_value, num_of_turns) VALUES (0,"asdf", 10, 2)')
    db.display_all_records("Agents")
