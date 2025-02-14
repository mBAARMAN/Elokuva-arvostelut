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
    genre TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE ratings (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value INTEGER CHECK(value BETWEEN 1 AND 5) UNIQUE
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies,
    user_id INTEGER REFERENCES users,
    rating_id INTEGER REFERENCES ratings(id),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);