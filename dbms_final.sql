create database research_hub;
use research_hub;

/* users */

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role ENUM('student', 'professor', 'admin') NOT NULL,
    department VARCHAR(255),
    research_interests TEXT,
    experience_level ENUM('beginner', 'intermediate', 'advanced'), 
    password VARCHAR(255) NOT NULL
);

/* projects */

CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INT,
    status ENUM('ongoing', 'completed') DEFAULT 'ongoing',
    FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
);

/* Collab Requests */

CREATE TABLE collaboration_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    professor_id INT,
    student_id INT,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (professor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE
);


/* community portal like twitter */

CREATE TABLE forum_posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id INT,
    category ENUM('General Research', 'Funding', 'Publication Help', 'Research Groups'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE CASCADE
);


/*  Research Highlights */

CREATE TABLE research_highlights (
    highlight_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    contributors TEXT,
    posted_by INT,
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (posted_by) REFERENCES users(user_id) ON DELETE CASCADE
);



