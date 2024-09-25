import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
 
# Initialize session state for login status and current page
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'  # Default to login page
 
# File paths
user_data_file = 'user_data.json'
 
# Function to load user data from JSON
def load_user_data():
    try:
        with open(user_data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
 
# Function to save user data to JSON
def save_user_data(user_data):
    with open(user_data_file, 'w') as file:
        json.dump(user_data, file, indent=4)
 
# Function to create a folder for the user
def create_user_folder(username):
    user_folder = f"users/{username}"
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return user_folder
 
# Function to handle login page
def login_page():
    st.title("Login")
 
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type='password', key="login_password")
    if st.button("Submit", key="login_submit"):
        user_data = load_user_data()
 
        if username in user_data and user_data[username]['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"Login successful! Welcome {username}")
            create_user_folder(username)
            st.session_state['page'] = 'marks'  # Navigate to marks page
        else:
            st.error("Invalid username or password.")
 
# Function to handle signup page
def signup_page():
    st.title("Signup")
 
    username = st.text_input("New Username", key="signup_username")
    password = st.text_input("New Password", type='password', key="signup_password")
    mobile = st.text_input("Mobile Number", key="signup_mobile")
    city = st.text_input("City", key="signup_city")
 
    if st.button("Sign Up", key="signup_submit"):
        user_data = load_user_data()
 
        if username in user_data:
            st.error("Username already exists. Please choose a different username.")
        else:
            user_data[username] = {
                'password': password,
                'mobile': mobile,
                'city': city
            }
            save_user_data(user_data)
            st.success(f"Signed up successfully as {username}")
            st.session_state['page'] = 'login'  # Redirect to login after signup
 
# Function to handle marks entry page
def marks_page():
    st.title(f"Enter Marks for {st.session_state['username']}")
 
    subjects = ['Math', 'English', 'Chemistry', 'Physics', 'Biology', 'Geography', 'Economics']
    marks = {}
   
    for subject in subjects:
        marks[subject] = st.number_input(f"Enter marks for {subject}", min_value=0, max_value=100)
 
    if st.button("Submit Marks"):
        user_folder = create_user_folder(st.session_state['username'])
        marks_file = os.path.join(user_folder, f"{st.session_state['username']}.csv")
 
        # Save marks to CSV
        marks_df = pd.DataFrame([marks])
        marks_df.to_csv(marks_file, index=False, mode='a', header=not os.path.exists(marks_file))
       
        st.session_state['marks'] = marks_df
        st.success("Marks submitted successfully!")
 
# Function to plot graphs for user marks
def plot_graphs():
    st.title(f"Graphs for {st.session_state['username']}'s Marks")
   
    # Load marks
    user_folder = create_user_folder(st.session_state['username'])
    marks_file = os.path.join(user_folder, f"{st.session_state['username']}.csv")
    marks_df = pd.read_csv(marks_file)
 
    # 1. Bar graph of average marks
    avg_marks = marks_df.mean(axis=0)
    bar_fig = px.bar(x=avg_marks.index, y=avg_marks.values, title="Average Marks")
    st.plotly_chart(bar_fig)
 
    # 2. Line graph of marks as per each subject
    line_fig = px.line(marks_df.T, y=marks_df.T[0], title="Marks per Subject", labels={'y': 'Marks', 'index': 'Subjects'})
    st.plotly_chart(line_fig)
 
    # 3. Pie chart of marks as per each subject
    pie_fig = px.pie(names=marks_df.columns, values=marks_df.iloc[0], title="Marks Distribution")
    st.plotly_chart(pie_fig)
 
# Control navigation between login, signup, marks entry, and graphs pages
st.sidebar.title("User Options")
 
if st.sidebar.button("Login", key="login_button"):
    st.session_state['page'] = 'login'
 
if st.sidebar.button("Signup", key="signup_button"):
    st.session_state['page'] = 'signup'
 
# Display either login, signup, marks, or graphs page based on the current session state
if st.session_state['page'] == 'login':
    login_page()
elif st.session_state['page'] == 'signup':
    signup_page()
elif st.session_state['page'] == 'marks' and st.session_state.get('logged_in'):
    marks_page()
elif st.session_state['page'] == 'graphs' and st.session_state.get('logged_in'):
    plot_graphs()
 
# If user is logged in, display additional content
if st.session_state['logged_in']:
    st.sidebar.write(f"Logged in as: {st.session_state['username']}")
   
    # Add button to take the user to the marks page
    if st.sidebar.button("Enter Marks", key="enter_marks_button"):
        st.session_state['page'] = 'marks'
 
    # Add button to take the user to the graphs page
    if st.sidebar.button("Show Graphs", key="show_graphs_button"):
        st.session_state['page'] = 'graphs'
 
    # Add sign-out button
    if st.sidebar.button("Sign Out", key="sign_out_button"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['page'] = 'login'
        st.success("Signed out successfully!")
 