DROP DATABASE IF EXISTS beedb;
CREATE DATABASE beedb;

USE beedb;

DROP TABLE IF EXISTS experiment_meta;
CREATE TABLE experiment_meta
(
    HiveID                      int unsigned NOT NULL,
    ExperimentNum               int unsigned NOT NULL,
    HiveType                    int unsigned NOT NULL,

    PRIMARY KEY                 ( HiveID )
);

DROP TABLE IF EXISTS bees;
CREATE TABLE bees
(
    BeeID                       int unsigned NOT NULL,
    TagID                       int unsigned NOT NULL,
    TagConfidence               float NOT NULL,
    NumTagClassified            int unsigned NOT NULL,
    LengthTracked               int unsigned NOT NULL,
    HiveID                      int unsigned NOT NULL,
    HourBin                     DATETIME NOT NULL,

    PRIMARY KEY                 ( BeeID ),
    FOREIGN KEY                 ( HiveID )                          REFERENCES          experiment_meta ( HiveID )
);

DROP TABLE IF EXISTS paths;
CREATE TABLE paths
(
    PathID                      int unsigned NOT NULL,
    BeeID                       int unsigned NOT NULL,
    StartPathFrame              int unsigned NOT NULL,
    EndPathFrame                int unsigned NOT NULL,

    PRIMARY KEY                 ( PathID ),
    FOREIGN KEY                 ( BeeID )                           REFERENCES          bees ( BeeID )
);

DROP TABLE IF EXISTS bee_coords;
CREATE TABLE bee_coords
(
    PathID                      int unsigned NOT NULL,
    Frame                       int unsigned NOT NULL,
    X                           float NOT NULL,
    Y                           float NOT NULL,

    PRIMARY KEY                 ( PathID, Frame ),
    FOREIGN KEY                 ( PathID )                          REFERENCES          paths ( PathID )
);
