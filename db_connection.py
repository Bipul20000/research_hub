
import mysql.connector
import streamlit as st
from datetime import datetime


# Function to connect to the database
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",  # Replace with your MySQL host
        user="root",  # Replace with your MySQL username
        password="bipul2576",  # Replace with your MySQL password
        database="research_hub"
    )


# Function to fetch user details for login
def get_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    conn.close()
    return user


# Function to register a new user
def register_user(name, email, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if email is already registered
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        conn.close()
        return False  # Email already exists

    query = "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, email, password, role))
    conn.commit()
    conn.close()
    return True  # Registration successful


# Function to fetch research highlights
def get_research_highlights():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT rh.title, rh.summary, rh.contributors, rh.date_posted, u.name AS posted_by
        FROM research_highlights rh
        JOIN users u ON rh.posted_by = u.user_id
        ORDER BY rh.date_posted DESC
    """
    cursor.execute(query)
    highlights = cursor.fetchall()
    conn.close()
    return highlights


# Function to search research highlights by keyword
def search_research_highlights(keyword):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT rh.title, rh.summary, rh.contributors, rh.date_posted, u.name AS posted_by
        FROM research_highlights rh
        JOIN users u ON rh.posted_by = u.user_id
        WHERE rh.title LIKE %s OR rh.summary LIKE %s OR rh.contributors LIKE %s
        ORDER BY rh.date_posted DESC
    """
    search_term = f"%{keyword}%"
    cursor.execute(query, (search_term, search_term, search_term))
    highlights = cursor.fetchall()
    conn.close()
    return highlights


def update_user_profile(user_id, department, research_interests, experience_level=None, photo_data=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Start building the base parameters that are always included
    params = [department, research_interests]
    query = "UPDATE users SET department=%s, research_interests=%s"

    # Add experience_level if provided
    if experience_level:
        query += ", experience_level=%s"
        params.append(experience_level)

    # Add photo_data if provided
    if photo_data is not None:
        query += ", profile_photo=%s"
        params.append(photo_data)

    # Add the WHERE clause
    query += " WHERE user_id=%s"
    params.append(user_id)

    # Execute the query
    cursor.execute(query, tuple(params))

    conn.commit()
    conn.close()
    return True


# Function to send a collaboration request

def send_collaboration_request(student_id, professor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if a request already exists with any status (pending, accepted, or rejected)
    cursor.execute(
        "SELECT * FROM collaboration_requests WHERE student_id = %s AND professor_id = %s",
        (student_id, professor_id)
    )

    # Fetching the result to ensure there are no unread results
    existing_request = cursor.fetchone()

    # After fetching the result, clear the cursor (optional but good practice)
    cursor.fetchall()

    if existing_request:
        # If the request is already accepted, prevent sending a new request
        if existing_request['status'] == 'accepted':
            conn.close()
            return False  # Request already accepted, can't send a new one
        elif existing_request['status'] == 'rejected':
            # If the request was rejected, allow sending a new request by updating the existing one
            cursor.execute(
                "UPDATE collaboration_requests SET status = 'pending' WHERE student_id = %s AND professor_id = %s",
                (student_id, professor_id)
            )
            conn.commit()
            conn.close()
            return True  # Request renewed successfully
        else:
            # If status is pending, don't create a duplicate
            conn.close()
            return False  # Request already pending
    else:
        # Insert new request
        query = "INSERT INTO collaboration_requests (student_id, professor_id, status) VALUES (%s, %s, 'pending')"
        cursor.execute(query, (student_id, professor_id))
        conn.commit()
        conn.close()
        return True  # Request sent successfully


# Function to fetch pending requests for a professor
def get_pending_requests(professor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT cr.request_id, u.name AS student_name, u.email, u.research_interests
        FROM collaboration_requests cr
        JOIN users u ON cr.student_id = u.user_id
        WHERE cr.professor_id = %s AND cr.status = 'pending'
    """
    cursor.execute(query, (professor_id,))
    requests = cursor.fetchall()
    conn.close()
    return requests


# Function to update request status (accept/reject)
def update_request_status(request_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE collaboration_requests SET status = %s WHERE request_id = %s"
    cursor.execute(query, (status, request_id))
    conn.commit()
    conn.close()
    return True


# Function to get active collaborations for a user
def get_active_collaborations(user_id, role):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if role == "student":
        query = """
            SELECT cr.request_id, u.name, u.department, u.research_interests, u.user_id as professor_id
            FROM collaboration_requests cr
            JOIN users u ON cr.professor_id = u.user_id
            WHERE cr.student_id = %s AND cr.status = 'accepted'
        """
    else:  # professor
        query = """
            SELECT cr.request_id, u.name, u.department, u.research_interests, u.experience_level, u.user_id as student_id
            FROM collaboration_requests cr
            JOIN users u ON cr.student_id = u.user_id
            WHERE cr.professor_id = %s AND cr.status = 'accepted'
        """

    cursor.execute(query, (user_id,))
    collaborations = cursor.fetchall()
    conn.close()
    return collaborations


# Function to delete a collaboration
def delete_collaboration(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "DELETE FROM collaboration_requests WHERE request_id = %s"
    cursor.execute(query, (request_id,))
    conn.commit()
    conn.close()
    return True


# Function to get all forum posts
def get_forum_posts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.post_id, p.title, p.content, p.category, p.created_at, 
               u.name AS author_name, u.role AS author_role
        FROM forum_posts p
        JOIN users u ON p.author_id = u.user_id
        ORDER BY p.created_at DESC
    """
    cursor.execute(query)
    posts = cursor.fetchall()
    conn.close()
    return posts


# Function to get forum posts by category
def get_forum_posts_by_category(category):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.post_id, p.title, p.content, p.category, p.created_at, 
               u.name AS author_name, u.role AS author_role
        FROM forum_posts p
        JOIN users u ON p.author_id = u.user_id
        WHERE p.category = %s
        ORDER BY p.created_at DESC
    """
    cursor.execute(query, (category,))
    posts = cursor.fetchall()
    conn.close()
    return posts


# Function to create a new forum post
def create_forum_post(title, content, author_id, category):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO forum_posts (title, content, author_id, category) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (title, content, author_id, category))
    conn.commit()
    conn.close()
    return True


# Function to recommend professors based on student interests
def recommend_professors(student_interests):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT user_id, name, department, research_interests
        FROM users
        WHERE role = 'professor' AND research_interests IS NOT NULL
        ORDER BY user_id
    """
    cursor.execute(query)
    professors = cursor.fetchall()
    conn.close()

    # Simple recommendation system based on keyword matching
    recommendations = []
    interests_lower = student_interests.lower()

    for prof in professors:
        # Calculate a simple compatibility score based on keyword matching
        if prof['research_interests']:
            prof_interests_lower = prof['research_interests'].lower()
            interests_keywords = [keyword.strip() for keyword in interests_lower.split(',')]
            prof_keywords = [keyword.strip() for keyword in prof_interests_lower.split(',')]

            # Count matching keywords
            matches = sum(1 for keyword in interests_keywords if any(keyword in prof_kw for prof_kw in prof_keywords))
            if matches > 0:
                # Calculate a simple score from 0-100
                score = min(int((matches / len(interests_keywords)) * 100), 100)
                prof['compatibility'] = score
                recommendations.append(prof)

    # Sort by compatibility score
    recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
    return recommendations


# Function to find potential student research partners
def find_research_partners(student_id, department, interests):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT user_id, name, department, research_interests, experience_level
        FROM users
        WHERE role = 'student' AND user_id != %s AND research_interests IS NOT NULL
        ORDER BY user_id
    """
    cursor.execute(query, (student_id,))
    students = cursor.fetchall()
    conn.close()

    # Simple matching system based on interests and department
    partners = []
    interests_lower = interests.lower()

    for student in students:
        if student['research_interests']:
            student_interests_lower = student['research_interests'].lower()

            # Calculate match score (department match + interests overlap)
            dept_match = 30 if student['department'] == department else 0

            # Calculate interests overlap
            interests_keywords = [keyword.strip() for keyword in interests_lower.split(',')]
            student_keywords = [keyword.strip() for keyword in student_interests_lower.split(',')]

            # Count matching keywords
            matches = sum(
                1 for keyword in interests_keywords if any(keyword in student_kw for student_kw in student_keywords))
            interest_score = min(int((matches / max(len(interests_keywords), 1)) * 70), 70)

            total_score = dept_match + interest_score
            if total_score > 0:
                student['compatibility'] = total_score
                partners.append(student)

    # Sort by compatibility score
    partners.sort(key=lambda x: x['compatibility'], reverse=True)
    return partners


# Function to get projects by user (user_id)
def get_user_projects(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM projects WHERE owner_id = %s"
    cursor.execute(query, (user_id,))
    projects = cursor.fetchall()
    conn.close()
    return projects


# Function to add a new project
def add_new_project(title, description, status, owner_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO projects (title, description, status, owner_id) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (title, description, status, owner_id))
    conn.commit()
    conn.close()
    return True


# Function to update a project
def update_project(project_id, title, description, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE projects SET title = %s, description = %s, status = %s WHERE project_id = %s"
    cursor.execute(query, (title, description, status, project_id))
    conn.commit()
    conn.close()
    return True


# Function to get a specific project by ID
def get_project_by_id(project_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM projects WHERE project_id = %s"
    cursor.execute(query, (project_id,))
    project = cursor.fetchone()
    conn.close()
    return project









# import mysql.connector
# import streamlit as st
# from datetime import datetime
#
#
# # Function to connect to the database
# def get_db_connection():
#     return mysql.connector.connect(
#         host="127.0.0.1",  # Replace with your MySQL host
#         user="root",  # Replace with your MySQL username
#         password="bipul2576",  # Replace with your MySQL password
#         database="research_hub"
#     )
#
#
# # Function to fetch user details for login
# def get_user(email, password):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = "SELECT * FROM users WHERE email = %s AND password = %s"
#     cursor.execute(query, (email, password))
#     user = cursor.fetchone()
#     conn.close()
#     return user
#
#
# # Function to register a new user
# def register_user(name, email, password, role):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     # Check if email is already registered
#     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#     if cursor.fetchone():
#         conn.close()
#         return False  # Email already exists
#
#     query = "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)"
#     cursor.execute(query, (name, email, password, role))
#     conn.commit()
#     conn.close()
#     return True  # Registration successful
#
#
# # Function to fetch research highlights
# def get_research_highlights():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = """
#         SELECT rh.title, rh.summary, rh.contributors, rh.date_posted, u.name AS posted_by
#         FROM research_highlights rh
#         JOIN users u ON rh.posted_by = u.user_id
#         ORDER BY rh.date_posted DESC
#     """
#     cursor.execute(query)
#     highlights = cursor.fetchall()
#     conn.close()
#     return highlights
#
#
# # Function to search research highlights by keyword
# def search_research_highlights(keyword):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = """
#         SELECT rh.title, rh.summary, rh.contributors, rh.date_posted, u.name AS posted_by
#         FROM research_highlights rh
#         JOIN users u ON rh.posted_by = u.user_id
#         WHERE rh.title LIKE %s OR rh.summary LIKE %s OR rh.contributors LIKE %s
#         ORDER BY rh.date_posted DESC
#     """
#     search_term = f"%{keyword}%"
#     cursor.execute(query, (search_term, search_term, search_term))
#     highlights = cursor.fetchall()
#     conn.close()
#     return highlights
#
#
# def update_user_profile(user_id, department, research_interests, experience_level=None, photo_data=None):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     # Start building the base parameters that are always included
#     params = [department, research_interests]
#     query = "UPDATE users SET department=%s, research_interests=%s"
#
#     # Add experience_level if provided
#     if experience_level:
#         query += ", experience_level=%s"
#         params.append(experience_level)
#
#     # Add photo_data if provided
#     if photo_data is not None:
#         query += ", profile_photo=%s"
#         params.append(photo_data)
#
#     # Add the WHERE clause
#     query += " WHERE user_id=%s"
#     params.append(user_id)
#
#     # Execute the query
#     cursor.execute(query, tuple(params))
#
#     conn.commit()
#     conn.close()
#     return True
#
#
# # Function to send a collaboration request
# def send_collaboration_request(student_id, professor_id):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)  # Ensure we get dictionaries instead of tuples
#
#     # Check if a request already exists with any status (pending, accepted, or rejected)
#     cursor.execute(
#         "SELECT * FROM collaboration_requests WHERE student_id = %s AND professor_id = %s",
#         (student_id, professor_id)
#     )
#
#     existing_request = cursor.fetchone()
#
#     if existing_request:
#         # If the request already exists and is either accepted or rejected, prevent the new request
#         if existing_request['status'] in ['accepted', 'rejected']:
#             conn.close()
#             return False  # Request already processed (accepted or rejected)
#
#     # Insert new request if no existing request or it is pending
#     query = "INSERT INTO collaboration_requests (student_id, professor_id, status) VALUES (%s, %s, 'pending')"
#     cursor.execute(query, (student_id, professor_id))
#     conn.commit()
#     conn.close()
#     return True
#  # Request sent successfully
#
#
# # Function to fetch pending requests for a professor
# def get_pending_requests(professor_id):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = """
#         SELECT cr.request_id, u.name AS student_name, u.email, u.research_interests
#         FROM collaboration_requests cr
#         JOIN users u ON cr.student_id = u.user_id
#         WHERE cr.professor_id = %s AND cr.status = 'pending'
#     """
#     cursor.execute(query, (professor_id,))
#     requests = cursor.fetchall()
#     conn.close()
#     return requests
#
#
# # Function to update request status (accept/reject)
# def update_request_status(request_id, status):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     query = "UPDATE collaboration_requests SET status = %s WHERE request_id = %s"
#     cursor.execute(query, (status, request_id))
#     conn.commit()
#     conn.close()
#     return True
#
#
# # Function to get active collaborations for a user
# def get_active_collaborations(user_id, role):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#
#     if role == "student":
#         query = """
#             SELECT cr.request_id, u.name, u.department, u.research_interests
#             FROM collaboration_requests cr
#             JOIN users u ON cr.professor_id = u.user_id
#             WHERE cr.student_id = %s AND cr.status = 'accepted'
#         """
#     else:  # professor
#         query = """
#             SELECT cr.request_id, u.name, u.department, u.research_interests, u.experience_level
#             FROM collaboration_requests cr
#             JOIN users u ON cr.student_id = u.user_id
#             WHERE cr.professor_id = %s AND cr.status = 'accepted'
#         """
#
#     cursor.execute(query, (user_id,))
#     collaborations = cursor.fetchall()
#     conn.close()
#     return collaborations
#
#
# # Function to get all forum posts
# def get_forum_posts():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = """
#         SELECT p.post_id, p.title, p.content, p.category, p.created_at,
#                u.name AS author_name, u.role AS author_role
#         FROM forum_posts p
#         JOIN users u ON p.author_id = u.user_id
#         ORDER BY p.created_at DESC
#     """
#     cursor.execute(query)
#     posts = cursor.fetchall()
#     conn.close()
#     return posts
#
#
# # Function to get forum posts by category
# def get_forum_posts_by_category(category):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = """
#         SELECT p.post_id, p.title, p.content, p.category, p.created_at,
#                u.name AS author_name, u.role AS author_role
#         FROM forum_posts p
#         JOIN users u ON p.author_id = u.user_id
#         WHERE p.category = %s
#         ORDER BY p.created_at DESC
#     """
#     cursor.execute(query, (category,))
#     posts = cursor.fetchall()
#     conn.close()
#     return posts
#
#
# # Function to create a new forum post
# def create_forum_post(title, content, author_id, category):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     query = "INSERT INTO forum_posts (title, content, author_id, category) VALUES (%s, %s, %s, %s)"
#     cursor.execute(query, (title, content, author_id, category))
#     conn.commit()
#     conn.close()
#     return True
#
#
# # Function to recommend professors based on student interests
# def recommend_professors(student_interests):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = """
#         SELECT user_id, name, department, research_interests
#         FROM users
#         WHERE role = 'professor' AND research_interests IS NOT NULL
#         ORDER BY user_id
#     """
#     cursor.execute(query)
#     professors = cursor.fetchall()
#     conn.close()
#
#     # Simple recommendation system based on keyword matching
#     recommendations = []
#     interests_lower = student_interests.lower()
#
#     for prof in professors:
#         # Calculate a simple compatibility score based on keyword matching
#         if prof['research_interests']:
#             prof_interests_lower = prof['research_interests'].lower()
#             interests_keywords = [keyword.strip() for keyword in interests_lower.split(',')]
#             prof_keywords = [keyword.strip() for keyword in prof_interests_lower.split(',')]
#
#             # Count matching keywords
#             matches = sum(1 for keyword in interests_keywords if any(keyword in prof_kw for prof_kw in prof_keywords))
#             if matches > 0:
#                 # Calculate a simple score from 0-100
#                 score = min(int((matches / len(interests_keywords)) * 100), 100)
#                 prof['compatibility'] = score
#                 recommendations.append(prof)
#
#     # Sort by compatibility score
#     recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
#     return recommendations
#
#
# # Function to find potential student research partners
# def find_research_partners(student_id, department, interests):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = """
#         SELECT user_id, name, department, research_interests, experience_level
#         FROM users
#         WHERE role = 'student' AND user_id != %s AND research_interests IS NOT NULL
#         ORDER BY user_id
#     """
#     cursor.execute(query, (student_id,))
#     students = cursor.fetchall()
#     conn.close()
#
#     # Simple matching system based on interests and department
#     partners = []
#     interests_lower = interests.lower()
#
#     for student in students:
#         if student['research_interests']:
#             student_interests_lower = student['research_interests'].lower()
#
#             # Calculate match score (department match + interests overlap)
#             dept_match = 30 if student['department'] == department else 0
#
#             # Calculate interests overlap
#             interests_keywords = [keyword.strip() for keyword in interests_lower.split(',')]
#             student_keywords = [keyword.strip() for keyword in student_interests_lower.split(',')]
#
#             # Count matching keywords
#             matches = sum(
#                 1 for keyword in interests_keywords if any(keyword in student_kw for student_kw in student_keywords))
#             interest_score = min(int((matches / max(len(interests_keywords), 1)) * 70), 70)
#
#             total_score = dept_match + interest_score
#             if total_score > 0:
#                 student['compatibility'] = total_score
#                 partners.append(student)
#
#     # Sort by compatibility score
#     partners.sort(key=lambda x: x['compatibility'], reverse=True)
#     return partners
#
# # Function to get projects by student (user_id)
# def get_user_projects(user_id):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = "SELECT * FROM projects WHERE owner_id = %s"
#     cursor.execute(query, (user_id,))
#     projects = cursor.fetchall()
#     conn.close()
#     return projects
#
#
# # Function to add a new project
# def add_new_project(title, description, status, owner_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     query = "INSERT INTO projects (title, description, status, owner_id) VALUES (%s, %s, %s, %s)"
#     cursor.execute(query, (title, description, status, owner_id))
#     conn.commit()
#     conn.close()
#     return True
#
