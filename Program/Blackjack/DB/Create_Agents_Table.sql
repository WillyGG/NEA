CREATE TABLE Agents (
    agent_id INTEGER PRIMARY KEY,
    agent_name varchar(255) NOT NULL,
    description TEXT,
    games_won INTEGER NOT NULL DEFAULT 0,
    games_played INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE country (
    id VARCHAR(2) NOT NULL,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY(id)
 );