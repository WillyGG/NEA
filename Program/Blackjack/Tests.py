import sys, os
sys.path.append(os.path.realpath("./DB"))
from DB_Wrapper import DB_Wrapper
from Deck import Deck
from Card_Counter import Card_Counter
from Comparison_Tool import Comparison_Tool

class T:
    def __init__(self):
        self.db_wrapper = DB_Wrapper("DB/Blackjack.sqlite")

    def test_1ai(self):
        # proving the function of the card counter
        d = Deck()
        cc = Card_Counter()

        HAND_VALUE = 15
        WNR_VALUE = 17

        cc.displayCardRecord()
        print(cc.calcChances(HAND_VALUE, WNR_VALUE))
        for _ in range(5):
            print()
            card = d.pop()
            print(card)
            cc.decrement_card(card)
            cc.displayCardRecord()
            print(cc.calcChances(HAND_VALUE, WNR_VALUE))
        print(end="\n\n\n")

        # getting the moves from a game of the neural network and showing it's internal state
        r = []
        game_id = 999
        while len(r) < 3:
            r = []
            game_id += 1
            query = """
                    SELECT Moves.*, Card_Counter_Record.*
                    FROM Moves, Card_Counter_Record
                    WHERE Moves.game_id={0} AND Card_Counter_Record.game_id={0}
                          AND Moves.player_id="nn" AND Moves.turn_num=Card_Counter_Record.turn_num
                    """.format(game_id)

            result = self.db_wrapper.execute_queries(query, get_result=True)

            for move in result:
                r.append(move)
        for move in r:
            print(move)

    def test_1aii(self):
        results = []
        for game_id in range(1000,2000):
            move_query = """
                    SELECT * 
                    FROM Moves
                    WHERE game_id = {0} AND hand_val_before=17 AND player_id="nn"
                    """.format(game_id)


            move = self.db_wrapper.execute_queries(move_query, get_result=True)
            if move == []:
                continue
            turn_num = move[0][2]
            cc_rec_query = """
                           SELECT *
                           FROM Card_Counter_Record
                           WHERE game_id={0} AND turn_num={1}
                           """.format(game_id, turn_num)

            cc_rec = self.db_wrapper.execute_queries(cc_rec_query, get_result=True)
            results.append(move + cc_rec)

        for result in results:
            print(result)
            print()

    def test_1aiii(self):
        lower_bound = 3105
        uppper_bound = 3150

        for agent in ["nn"]: #"cc_ai", "simple"]:
            q_21 = """
                    SELECT *       
                    FROM Moves
                    WHERE game_id < {1} AND game_id > {0} AND hand_val_before=21 AND player_id="{2}"
                   """.format(lower_bound, uppper_bound, agent)

            q_lt_12 = """
                      SELECT * 
                      FROM Moves
                      WHERE game_id < {1} AND game_id > {0} AND hand_val_before<=11 AND player_id="{2}"
                      """.format(lower_bound, uppper_bound, agent)

            res_21 = self.db_wrapper.execute_queries(q_21, get_result=True)
            res_lt_12 = self.db_wrapper.execute_queries(q_lt_12, get_result=True)

            for move in res_21:
                print(move)
            print(end="\n")
            for move in res_lt_12:
                print(move)
            print(end="\n\n")

    #todo come bak to this when you create a console blackjack environment
    def test_1bi(self):
        query = """
                UPDATE users
                SET games_played=1, games_won=1
                WHERE username="admin";
                
                UPDATE users
                SET games_played=1, games_won=0
                WHERE username="mr_aqa";
                """
        self.db_wrapper.execute_queries(query)

        ct = Comparison_Tool()
        ids = ["nn", "cc_ai", "simple", "mr_aqa", "admin"]
        for id in ids:
            print(id)
            ct.output_player_wr(id)

    def test_2ai(self):
        ct = Comparison_Tool()
        user = "slakdjlafd"
        aggr = ct.get_aggression_rating(user)
        if aggr == None:
            print("pass")

if __name__ == "__main__":
    t = T()
    t.test_2ai()