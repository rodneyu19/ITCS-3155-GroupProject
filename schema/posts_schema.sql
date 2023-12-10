CREATE TABLE IF NOT EXISTS users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(16) NOT NULL UNIQUE,
	password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS post (
	post_id SERIAL PRIMARY KEY,
	title VARCHAR(255) NOT NULL,
	body TEXT NOT NULL,
	user_id INT,
    	link VARCHAR(255),
	FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS comments (
	comment_id SERIAL PRIMARY KEY,
	comment TEXT NOT NULL,
	user_id INT,
	post_id INT,
	FOREIGN KEY (user_id) REFERENCES users (user_id),
	FOREIGN KEY (post_id) REFERENCES post (post_id)
);
