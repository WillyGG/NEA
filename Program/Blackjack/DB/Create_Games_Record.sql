CREATE TABLE Game_Record (
    game_id INTEGER NOT NULL,
    winner_id varchar(255) NOT NULL,
    winning_hand TEXT NOT NULL,
    winning_hand_value INTEGER NOT NULL,
    num_of_turns INTEGER NOT NULL,
    PRIMARY KEY(game_id)
);

CREATE TABLE Player_ids (
    player_1 varchar(255) DEFAULT NULL,
    player_2 varchar(255) DEFAULT NULL,
    player_3 varchar(255) DEFAULT NULL,
    player_4 varchar(255) DEFAULT NULL,
    player_5 varchar(255) DEFAULT NULL,
    player_6 varchar(255) DEFAULT NULL,
    player_7 varchar(255) DEFAULT NULL,
    player_8 varchar(255) DEFAULT NULL,

    FOREIGN KEY (game_id) REFERENCES Game_Record(game_id)
    PRIMARY KEY (game_id)
);

CREATE TABLE Moves (
    player_id varchar(255) NOT NULL,
    game_id INTEGER NOT NULL,
    turn_num INTEGER NOT NULL,
    hand TEXT NOT NULL,
    move BIT NOT Null, -- 1 -> Hit, 0 -> False
    FOREIGN KEY (game_id) REFERENCES Game_Record(game_id)
    PRIMARY KEY(player_id, game_id, turn_num)
);
