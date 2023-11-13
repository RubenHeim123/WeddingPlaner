-- CREATE TABLE IF NOT EXISTS wedding (
--     id INTEGER PRIMARY KEY,
--     title TEXT NOT NULL,
--     bride_name TEXT,
--     groom_name TEXT,
--     wedding_date DATE,
--     location TEXT,
--     user_id INTEGER NOT NULL,
--     FOREIGN KEY (user_id) REFERENCES user(id)
-- );
-- CREATE TABLE users (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     username TEXT NOT NULL UNIQUE,
--     hash TEXT NOT NULL
-- );
-- SELECT * FROM sqlite_sequence
-- CREATE TABLE IF NOT EXISTS checklist (
--     id INTEGER PRIMARY KEY,
--     wedding_id INTEGER NOT NULL,
--     item TEXT NOT NULL,
--     completed BOOLEAN NOT NULL,
--     FOREIGN KEY (wedding_id) REFERENCES wedding(id)
-- );
-- CREATE TABLE IF NOT EXISTS transactions (
--     id INTEGER PRIMARY KEY,
--     wedding_id INTEGER NOT NULL,
--     transaction_type TEXT NOT NULL, 
--     amount INTEGER NOT NULL,
--     description TEXT,
--     date DATE NOT NULL,
--     icon TEXT, -- Pfad oder Bezeichnung des Icons
--     FOREIGN KEY (wedding_id) REFERENCES wedding(id)
-- );
CREATE TABLE guest (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    rsvp_checkbox INTEGER,
    wedding_id INTEGER,
    FOREIGN KEY (wedding_id) REFERENCES wedding (id)
);
