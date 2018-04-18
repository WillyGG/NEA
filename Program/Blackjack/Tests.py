import sys, os
sys.path.append(os.path.realpath("./DB"))
from DB_Wrapper import DB_Wrapper

class T:
    def __init__(self):
        self.db_wrapper = DB_Wrapper("DB/Blackjack.sqlite")

    def test_1aii(self):
        results = []
        for game_id in range(1000,2000):
            query = """
                    SELECT * FROM Moves
                    WHERE game_id = {0} AND hand_val_before=17 AND player_id="nn"
                    """.format(game_id)
            result = self.db_wrapper.execute_queries(query, get_result=True)
            if result != []:
                results.append([game_id] + result)
        for result in results:
            print(result)
            print()

if __name__ == "__main__":
    t = T()
    t.test_1aii()