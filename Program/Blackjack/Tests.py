from DB.DB_Wrapper import DB_Wrapper

class Testing:
    def __init__(self):
        self.db_wrapper = DB_Wrapper("DB/Blackjack.sqlite")

    def test_1aii(self):
        results = []
        for game_id in range(1000,1020):
            query = """
                    SELECT * FROM Moves
                    WHERE game_id = {0} AND hand_val_before=17
                    """.format(game_id)
            result = self.db_wrapper.execute_queries(query)
            results.append(result)
        for result in results:
            print(result)
            print()

t = Testing()
t.test_1aii()