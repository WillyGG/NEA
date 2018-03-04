CREATE TABLE Game_Record (
    game_id INTEGER NOT NULL,
    winner_id INTEGER NOT NULL,
    winning_hand TEXT NOT NULL,
    winning_hand_value INTEGER NOT NULL,
    num_of_turns INTEGER NOT NULL,
    PRIMARY KEY(game_id)
);

CREATE TABLE Player_ids (
    player_1 INTEGER DEFAULT NULL,
    player_2 INTEGER DEFAULT NULL,
    player_3 INTEGER DEFAULT NULL,
    player_4 INTEGER DEFAULT NULL,
    player_5 INTEGER DEFAULT NULL,
    player_6 INTEGER DEFAULT NULL,
    player_7 INTEGER DEFAULT NULL,
    player_8 INTEGER DEFAULT NULL,

    FOREIGN KEY (game_id) REFERENCES Game_Record(game_id)
    PRIMARY KEY (game_id)
);

CREATE TABLE Moves (
    player_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    turn_num INTEGER NOT NULL,
    hand TEXT NOT NULL,
    move BIT NOT Null, -- 1 -> Hit, 0 -> False
    FOREIGN KEY (game_id) REFERENCES Game_Record(game_id)
    PRIMARY KEY(player_id, game_id, turn_num)
);
