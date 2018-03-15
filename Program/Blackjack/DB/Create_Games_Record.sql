CREATE TABLE Game_Record (
    game_id INTEGER NOT NULL,
    winner_id varchar(255) NOT NULL,
    winning_hand TEXT NOT NULL,
    winning_hand_value INTEGER NOT NULL,
    num_of_turns INTEGER NOT NULL,
    players TEXT NOT NULL,
    PRIMARY KEY(game_id)
);

CREATE TABLE Moves (
    player_id varchar(255) NOT NULL,
    game_id INTEGER NOT NULL,
    turn_num INTEGER NOT NULL,
    next_best_val INTEGER,
    hand_val_before INTEGER NOT NULL,
    move BIT NOT Null, -- 1 -> Hit, 0 -> False
    hand_val_after INTEGER NOT NULL,
    FOREIGN KEY (game_id) REFERENCES Game_Record(game_id),
    PRIMARY KEY(player_id, game_id, turn_num)
);
