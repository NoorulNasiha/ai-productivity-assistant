CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    deadline TEXT,
    priority TEXT,
    status TEXT DEFAULT 'pending'
);
