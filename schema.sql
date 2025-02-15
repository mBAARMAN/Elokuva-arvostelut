CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title TEXT,
    director TEXT,
    year INTEGER,
    description TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE movie_classes (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies ON DELETE CASCADE,
    title TEXT,
    value TEXT
);

CREATE TABLE ratings (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value INTEGER CHECK(value BETWEEN 1 AND 5) UNIQUE
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    rating_id INTEGER REFERENCES ratings(id),
    review TEXT,
    created_at TIMESTAMP DEFAULT (DATETIME('now', '+2 hours'))
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    review_id INTEGER REFERENCES reviews ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    comment TEXT,
    created_at TIMESTAMP DEFAULT (DATETIME('now', '+2 hours'))
);
