CREATE TABLE IF NOT EXISTS post (
	post_id SERIAL PRIMARY KEY,
	title VARCHAR(255) NOT NULL,
	body TEXT NOT NULL,
	user_id INT
	FOREIGN KEY (user_id) REFERENCES (user_id)
);

CREATE TABLE IF NOT EXISTS users (
	user_id SERIAL PRIMARY KEY,
	username VARCHAR(16) NOT NULL,
	password VARCHAR(16) NOT NULL,
);

CREATE TABLE IF NOT EXISTS comments (
	comment_id SERIAL PRIMARY KEY,
	comment TEXT NOT NULL,
	user_id INT
	post_id INT
	FOREIGN KEY (user_id) REFERENCES (user_id)
	FOREIGN KEY (post_id) REFERENCES (post_id)
);
