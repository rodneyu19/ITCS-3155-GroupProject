CREATE TABLE post (
    post_id SERIAL NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    PRIMARY KEY (post_id)
);