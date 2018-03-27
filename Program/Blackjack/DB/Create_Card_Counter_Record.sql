CREATE TABLE IF NOT EXISTS Card_Counter_Record (
    game_id INTEGER NOT NULL,
    turn_num INTEGER NOT NULL,
    bust FLOAT NOT NULL,
    blackjack FLOAT NOT NULL,
    exceedWinningPlayer FLOAT NOT NULL,
    alreadyExceedingWinningPlayer BIT NOT NULL,
    move BIT NOT NULL,

    FOREIGN KEY (game_id) REFERENCES Game_Record(game_id),
    FOREIGN KEY (turn_num) REFERENCES Moves(turn_num),
    PRIMARY KEY(game_id, turn_num)
);