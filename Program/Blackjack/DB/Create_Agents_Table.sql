CREATE TABLE Agents (
    agent_id varchar(255) PRIMARY KEY,
    description TEXT,
    games_won INTEGER NOT NULL DEFAULT 0,
    games_played INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE country (
    id VARCHAR(2) NOT NULL,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY(id)
 );