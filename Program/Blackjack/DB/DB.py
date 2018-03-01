import sqlite3 as sq3

class DB:
    def __init__(self, db_path):
        self.db_path = db_path

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

    # execute passed query or passed array of queries
    def execute_queries(self, queries):
        # turns single query into executable form - defensive programming
        if isinstance(queries, str):
            queries = [queries]
        connection, cursor = self.connect_to_db(self.db_path)  # open connection
        try:
            for query in queries:
                cursor.execute(query)
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(e)
            return False

    def display_all_records(self, table_name):
        connection, cursor = self.connect_to_db(self.db_path)  # open connection
        query = "SELECT * FROM {0}".format(table_name)
        cursor.execute(query)
        rows = cursor.fetchall()
        connection.close()
        for row in rows:
            print(row)

if __name__ == "__main__":
    db = DB("Blackjack.sqlite")
    #db.execute_queries_from_file("Create_Agents_Table")
    #db.execute_queries_from_file("Populate_Agents")
    db.display_all_records("Agents")
