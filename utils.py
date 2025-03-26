import streamlit as st
import pandas as pd
import hashlib
import re

# Email validation
def is_valid_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

# Password strength check
def check_password_strength(password):
    """Check password strength and return feedback"""
    if len(password) < 8:
        return False, "Password should be at least 8 characters long"
    
    if not any(char.isdigit() for char in password):
        return False, "Password should contain at least one number"
    
    if not any(char.isupper() for char in password):
        return False, "Password should contain at least one uppercase letter"
    
    return True, "Password strength is good"

# Convert lists to dataframe
def list_to_dataframe(data_list, columns):
    """Convert a list of dictionaries to a pandas DataFrame with specified columns"""
    if not data_list:
        return pd.DataFrame(columns=columns)
    
    df = pd.DataFrame(data_list)
    
    # Ensure all required columns exist
    for col in columns:
        if col not in df.columns:
            df[col] = None
    
    # Select only the specified columns
    return df[columns]

# Format research interests for display
def format_interests(interests_string):
    """Convert comma-separated interests to a formatted list"""
    if not interests_string:
        return []
    
    interests = [interest.strip() for interest in interests_string.split(',') if interest.strip()]
    return interests

# Calculate match percentage between two users
def calculate_match_percentage(user1_interests, user2_interests):
    """Calculate the research interest match percentage between two users"""
    if not user1_interests or not user2_interests:
        return 0
    
    # Convert strings to lists if needed
    if isinstance(user1_interests, str):
        user1_interests = format_interests(user1_interests)
    if isinstance(user2_interests, str):
        user2_interests = format_interests(user2_interests)
    
    # Convert to lowercase for better matching
    user1_lower = [interest.lower() for interest in user1_interests]
    user2_lower = [interest.lower() for interest in user2_interests]
    
    # Find matching interests
    matches = 0
    for interest1 in user1_lower:
        for interest2 in user2_lower:
            # Check for exact match or if one contains the other
            if interest1 == interest2 or interest1 in interest2 or interest2 in interest1:
                matches += 1
                break
    
    # Calculate percentage (based on the smaller list)
    min_interests = min(len(user1_interests), len(user2_interests))
    if min_interests == 0:
        return 0
    
    return (matches / min_interests) * 100

# Create an abbreviation for long department names
def department_abbreviation(department):
    """Create an abbreviation for long department names"""
    if not department:
        return ""
    
    words = department.split()
    if len(words) == 1:
        return department[:3].upper()
    
    return ''.join(word[0].upper() for word in words)

# Generate a color based on a string (for consistent user colors)
def generate_color_from_string(s):
    """Generate a hex color code based on a string"""
    hash_value = hashlib.md5(s.encode()).hexdigest()
    r = int(hash_value[:2], 16) % 200 + 55  # Ensure color isn't too dark
    g = int(hash_value[2:4], 16) % 200 + 55
    b = int(hash_value[4:6], 16) % 200 + 55
    return f"#{r:02x}{g:02x}{b:02x}"
