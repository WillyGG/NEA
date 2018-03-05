CREATE TABLE users (
    username varchar(32) NOT NULL,
    password varchar(256) NOT NULL, -- store hashed password
    games_won INTEGER NOT NULL DEFAULT 0,
    games_played INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(username)
);