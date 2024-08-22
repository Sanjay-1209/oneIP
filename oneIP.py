import streamlit as st
import pandas as pd
from datetime import datetime

# Dummy data for employee names and credentials
employees = {
    "Lakshmi": "Lak@123",
    "Keerthana": "Kee@123",
    "Girija": "Gir@123",
    "Sadhana": "Sad@123",
    "Preetha": "Pre@123",
    "Mohan": "Moh@123",
    "Employee 7": "password7",
    "Employee 8": "password8",
    "Employee 9": "password9",
    "Employee 10": "password10"
}

# Salary details for each employee
employee_salaries = {
    "Lakshmi": 16000,
    "Keerthana": 12000,
    "Girija": 12000,
    "Sadhana": 16000,
    "Preetha": 12000,
    "Mohan": 12000
}

# Calculate daily salary
daily_salaries = {name: salary / 30 for name, salary in employee_salaries.items()}

# Dummy data for owner credentials
owner_credentials = {"username": "Shalini", "password": "Sha@Constramart"}

# Initialize session state for attendance DataFrame
if 'attendance_df' not in st.session_state:
    st.session_state.attendance_df = pd.DataFrame(columns=['Employee', 'Date', 'In-Punch', 'Out-Punch', 'Duration', 'Status', 'Daily Salary'])

# Function to calculate duration
def calculate_duration(in_punch, out_punch):
    if pd.notnull(in_punch) and pd.notnull(out_punch):
        return (out_punch - in_punch).total_seconds() / 3600  # Duration in hours
    return None

# Function to determine employee status
def determine_status(duration):
    if duration is None:
        return "Absent"
    elif duration >= 8:
        return "Present"
    else:
        return "Half-Day"

# Function to calculate daily salary based on status
def calculate_daily_salary(status, name):
    if status == "Present":
        return daily_salaries.get(name, 0)
    elif status == "Half-Day":
        return daily_salaries.get(name, 0) / 2
    return 0

# Function to update employee status and salary in the DataFrame
def update_employee_status_and_salary():
    df = st.session_state.attendance_df
    df['Duration'] = df.apply(lambda row: calculate_duration(row['In-Punch'], row['Out-Punch']), axis=1)
    df['Status'] = df['Duration'].apply(determine_status)
    df['Daily Salary'] = df.apply(lambda row: calculate_daily_salary(row['Status'], row['Employee']), axis=1)
    st.session_state.attendance_df = df

# Function to display the login page
def login_page():
    st.title("Login")
    
    user_type = st.radio("Login as:", ("Owner", "Employee"))
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if user_type == "Owner" and username == owner_credentials["username"] and password == owner_credentials["password"]:
            st.session_state.user_type = "Owner"
            st.experimental_rerun()
        elif user_type == "Employee" and username in employees and password == employees[username]:
            st.session_state.user_type = "Employee"
            st.session_state.current_employee = username
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# Function to display the owner page
def owner_page():
    st.title("Owner Dashboard")
    st.write("Attendance Records:")
    
    if st.session_state.attendance_df.empty:
        st.write("No attendance records found.")
    else:
        update_employee_status_and_salary()
        st.write(st.session_state.attendance_df)

# Function to display the employee page
def employee_page():
    st.title(f"Welcome, {st.session_state.current_employee}")
    
    date = st.date_input("Select Date", datetime.now())
    in_punch = st.time_input("In-Punch Time")
    out_punch = st.time_input("Out-Punch Time")
    
    if st.button("Submit Attendance"):
        new_data = {
            "Employee": st.session_state.current_employee,
            "Date": date,
            "In-Punch": datetime.combine(date, in_punch),
            "Out-Punch": datetime.combine(date, out_punch),
        }
        st.session_state.attendance_df = st.session_state.attendance_df.append(new_data, ignore_index=True)
        st.success("Attendance submitted successfully!")

# Main function to manage pages
def main():
    if 'user_type' not in st.session_state:
        login_page()
    elif st.session_state.user_type == "Owner":
        owner_page()
    elif st.session_state.user_type == "Employee":
        employee_page()

if __name__ == "__main__":
    main()
