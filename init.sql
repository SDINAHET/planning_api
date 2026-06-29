CREATE TABLE IF NOT EXISTS talks (
    id SERIAL PRIMARY KEY,
    day DATE NOT NULL,
    title TEXT NOT NULL,
    speaker TEXT,
    summary TEXT,
    room TEXT NOT NULL,
	start_time TIMESTAMPT NOT NULL,
	end_time TIMESTAMPT NOT NULL,
    url TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(day, room, start_time, title)
);
