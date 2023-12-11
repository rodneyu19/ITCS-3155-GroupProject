CREATE TABLE IF NOT EXISTS users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(16) NOT NULL UNIQUE,
	password VARCHAR(255) NOT NULL,
	firstname VARCHAR(16),
	lastname VARCHAR(16)
);

CREATE TABLE IF NOT EXISTS post (
	post_id SERIAL PRIMARY KEY,
	title VARCHAR(255) NOT NULL,
	body TEXT NOT NULL,
	id INT,
    	link VARCHAR(255),
	FOREIGN KEY (id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS comments (
	comment_id SERIAL PRIMARY KEY,
	comment TEXT NOT NULL,
	id INT,
	post_id INT,
	FOREIGN KEY (id) REFERENCES users (id),
	FOREIGN KEY (post_id) REFERENCES post (post_id)
);
