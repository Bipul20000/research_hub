import mysql.connector
import streamlit as st
import pandas as pd
from mysql.connector import Error
import os

# Initialize database connection
@st.cache_resource
def init_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "research_connect")
        )
        return conn
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

# Execute query with parameters
def execute_query(query, params=None, fetch=False):
    conn = init_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    except Error as e:
        st.error(f"Query execution error: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()

# Convert query results to dataframe
def query_to_dataframe(query, params=None):
    result = execute_query(query, params, fetch=True)
    if result:
        return pd.DataFrame(result)
    return pd.DataFrame()

# User management functions
def get_user_by_email(email):
    query = "SELECT * FROM users WHERE email = %s"
    result = execute_query(query, (email,), fetch=True)
    return result[0] if result else None

def get_user_by_id(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    result = execute_query(query, (user_id,), fetch=True)
    return result[0] if result else None

def create_user(name, email, password, role, department, research_interests, bio=""):
    query = """INSERT INTO users 
               (name, email, password, role, department, research_interests, bio) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    return execute_query(query, (name, email, password, role, department, research_interests, bio))

def update_user(user_id, name, department, research_interests, bio):
    query = """UPDATE users 
               SET name = %s, department = %s, research_interests = %s, bio = %s 
               WHERE id = %s"""
    return execute_query(query, (name, department, research_interests, bio, user_id))

# Search functions
def search_users(role=None, keywords=None, department=None):
    query = "SELECT id, name, role, department, research_interests, bio FROM users WHERE 1=1"
    params = []
    
    if role:
        query += " AND role = %s"
        params.append(role)
    
    if department:
        query += " AND department = %s"
        params.append(department)
    
    if keywords:
        query += " AND (research_interests LIKE %s OR bio LIKE %s)"
        keyword_param = f"%{keywords}%"
        params.extend([keyword_param, keyword_param])
    
    return execute_query(query, params, fetch=True)

# Project functions
def get_projects_by_user(user_id):
    query = """SELECT p.*, u.name as owner_name 
               FROM projects p
               JOIN users u ON p.owner_id = u.id
               WHERE p.owner_id = %s"""
    return execute_query(query, (user_id,), fetch=True)

def create_project(title, description, owner_id, status="Active"):
    query = """INSERT INTO projects 
               (title, description, owner_id, status, created_at) 
               VALUES (%s, %s, %s, %s, NOW())"""
    return execute_query(query, (title, description, owner_id, status))

def update_project(project_id, title, description, status):
    query = """UPDATE projects 
               SET title = %s, description = %s, status = %s 
               WHERE id = %s"""
    return execute_query(query, (title, description, status, project_id))

# Collaboration functions
def get_collaboration_requests(user_id, role):
    if role == "professor":
        query = """SELECT c.*, u.name as student_name, u.department as student_department 
                   FROM collaborations c
                   JOIN users u ON c.student_id = u.id
                   WHERE c.professor_id = %s"""
    else:
        query = """SELECT c.*, u.name as professor_name, u.department as professor_department 
                   FROM collaborations c
                   JOIN users u ON c.professor_id = u.id
                   WHERE c.student_id = %s"""
    return execute_query(query, (user_id,), fetch=True)

def create_collaboration_request(professor_id, student_id, message=""):
    query = """INSERT INTO collaborations 
               (professor_id, student_id, status, message, request_date) 
               VALUES (%s, %s, 'Pending', %s, NOW())"""
    return execute_query(query, (professor_id, student_id, message))

def update_collaboration_status(collaboration_id, status):
    query = "UPDATE collaborations SET status = %s WHERE id = %s"
    return execute_query(query, (status, collaboration_id))

# Forum functions
def get_forum_posts(category=None, limit=20):
    query = """SELECT p.*, u.name as author_name,
               (SELECT COUNT(*) FROM post_votes WHERE post_id = p.id AND vote_type = 'upvote') as upvotes,
               (SELECT COUNT(*) FROM post_votes WHERE post_id = p.id AND vote_type = 'downvote') as downvotes
               FROM forum_posts p
               JOIN users u ON p.author_id = u.id"""
    
    params = []
    if category:
        query += " WHERE p.category = %s"
        params.append(category)
    
    query += " ORDER BY p.created_at DESC LIMIT %s"
    params.append(limit)
    
    return execute_query(query, params, fetch=True)

def create_forum_post(title, content, author_id, category):
    query = """INSERT INTO forum_posts 
               (title, content, author_id, category, created_at) 
               VALUES (%s, %s, %s, %s, NOW())"""
    return execute_query(query, (title, content, author_id, category))

def vote_post(post_id, user_id, vote_type):
    # First remove any existing vote
    delete_query = "DELETE FROM post_votes WHERE post_id = %s AND user_id = %s"
    execute_query(delete_query, (post_id, user_id))
    
    # Then add the new vote
    insert_query = "INSERT INTO post_votes (post_id, user_id, vote_type) VALUES (%s, %s, %s)"
    return execute_query(insert_query, (post_id, user_id, vote_type))

# Research updates functions
def get_research_updates(featured_only=False, limit=10):
    query = """SELECT r.*, u.name as posted_by_name 
               FROM research_updates r
               JOIN users u ON r.posted_by = u.id"""
    
    params = []
    if featured_only:
        query += " WHERE r.featured = 1"
    
    query += " ORDER BY r.date_posted DESC LIMIT %s"
    params.append(limit)
    
    return execute_query(query, params, fetch=True)

def create_research_update(title, summary, contributors, posted_by, featured=False):
    query = """INSERT INTO research_updates 
               (title, summary, contributors, posted_by, featured, date_posted) 
               VALUES (%s, %s, %s, %s, %s, NOW())"""
    return execute_query(query, (title, summary, contributors, posted_by, featured))

def update_research_featured_status(update_id, featured):
    query = "UPDATE research_updates SET featured = %s WHERE id = %s"
    return execute_query(query, (featured, update_id))

# Department data
def get_all_departments():
    query = "SELECT DISTINCT department FROM users WHERE department IS NOT NULL AND department != ''"
    result = execute_query(query, fetch=True)
    if result:
        return [dept['department'] for dept in result]
    return []
