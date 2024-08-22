import streamlit as st
import pandas as pd
from datetime import datetime

# Allowed IP address
allowed_ip = "192.168.29.29"

# Get the client's IP address
client_ip = st.experimental_get_query_params().get('REMOTE_ADDR', ['192.168.29.29'])[0]

# Check if the client's IP matches the allowed IP
if client_ip != allowed_ip:
    st.error("Access Denied: This application can only be accessed from a specific IP address.")
else:
    # Your existing Streamlit code goes here
    
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

    def calculate_duration(in_punch, out_punch):
        if pd.notnull(in_punch) and pd.notnull(out_punch):
            return (out_punch - in_punch).total_seconds() / 3600  # Duration in hours
        return None

    def update_employee_status_and_salary():
        st.session_state.attendance_df['Duration'] = pd.to_numeric(st.session_state.attendance_df['Duration'], errors='coerce')  # Convert Duration to numeric

        for i, row in st.session_state.attendance_df.iterrows():
            if pd.notnull(row['Duration']):
                employee = row['Employee']
                if employee in daily_salaries:
                    if row['Duration'] >= 5:
                        status = "Full Day"
                        salary = daily_salaries[employee]
                    else:
                        status = "Half Day"
                        salary = daily_salaries[employee] / 2
                    st.session_state.attendance_df.at[i, 'Status'] = status
                    st.session_state.attendance_df.at[i, 'Daily Salary'] = salary
                else:
                    st.session_state.attendance_df.at[i, 'Status'] = "Unknown"
                    st.session_state.attendance_df.at[i, 'Daily Salary'] = 0

    def save_data():
        update_employee_status_and_salary()
        st.session_state.attendance_df.to_csv('attendance_records.csv', index=False)

    def load_data():
        try:
            st.session_state.attendance_df = pd.read_csv('attendance_records.csv')
            st.session_state.attendance_df['In-Punch'] = pd.to_datetime(st.session_state.attendance_df['In-Punch'], errors='coerce')
            st.session_state.attendance_df['Out-Punch'] = pd.to_datetime(st.session_state.attendance_df['Out-Punch'], errors='coerce')
        except FileNotFoundError:
            st.session_state.attendance_df = pd.DataFrame(columns=['Employee', 'Date', 'In-Punch', 'Out-Punch', 'Duration', 'Status', 'Daily Salary'])

    load_data()

    def format_datetime_columns(df):
        df['In-Punch'] = df['In-Punch'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['Out-Punch'] = df['Out-Punch'].dt.strftime('%Y-%m-%d %H:%M:%S')
        return df

    def login_page():
        st.title("Login")
        user_type = st.radio("Login as", ["Employee", "Owner"])
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

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

    def owner_page():
        st.title("Owner Dashboard")
        st.write("Attendance Records:")
        if st.session_state.attendance_df.empty:
            st.write("No attendance records found.")
        else:
            update_employee_status_and_salary()
            df_to_display = format_datetime_columns(st.session_state.attendance_df)
            st.dataframe(df_to_display[['Employee', 'Date', 'In-Punch', 'Out-Punch', 'Duration', 'Status', 'Daily Salary']])

    def employee_page():
        st.title(f"{st.session_state.current_employee}'s Attendance")
        today = datetime.now().strftime("%Y-%m-%d")
        employee_records = st.session_state.attendance_df[
            (st.session_state.attendance_df['Date'] == today) & 
            (st.session_state.attendance_df['Employee'] == st.session_state.current_employee)
        ]
        
        if not employee_records.empty:
            st.write("Your Punch In/Punch Out Records for Today:")
            df_to_display = format_datetime_columns(employee_records)
            st.dataframe(df_to_display[['Date', 'In-Punch', 'Out-Punch', 'Duration']])

        if st.button("Punch In"):
            if employee_records.empty or pd.notnull(employee_records.iloc[-1]['Out-Punch']):
                in_punch = datetime.now()
                st.session_state.attendance_df = st.session_state.attendance_df.append({
                    'Employee': st.session_state.current_employee,
                    'Date': today,
                    'In-Punch': in_punch,
                    'Out-Punch': None,
                    'Duration': None,
                    'Status': None,
                    'Daily Salary': 0
                }, ignore_index=True)
                st.success("Punched In")
                save_data()
            else:
                st.warning("You have already punched in today and have not punched out yet")
        
        if not employee_records.empty and pd.notnull(employee_records.iloc[-1]['In-Punch']) and pd.isnull(employee_records.iloc[-1]['Out-Punch']):
            if st.button("Punch Out"):
                out_punch = datetime.now()
                st.session_state.attendance_df.loc[
                    (st.session_state.attendance_df['Date'] == today) & 
                    (st.session_state.attendance_df['Employee'] == st.session_state.current_employee) & 
                    st.session_state.attendance_df['Out-Punch'].isnull(), 'Out-Punch'
                ] = out_punch
                st.session_state.attendance_df['In-Punch'] = pd.to_datetime(st.session_state.attendance_df['In-Punch'], errors='coerce')
                st.session_state.attendance_df['Out-Punch'] = pd.to_datetime(st.session_state.attendance_df['Out-Punch'], errors='coerce')
                st.session_state.attendance_df.loc[
                    (st.session_state.attendance_df['Date'] == today) & 
                    (st.session_state.attendance_df['Employee'] == st.session_state.current_employee), 'Duration'
                ] = st.session_state.attendance_df.apply(lambda row: calculate_duration(row['In-Punch'], row['Out-Punch']), axis=1)
                st.success("Punched Out")
                save_data()
        elif not employee_records.empty and pd.notnull(employee_records.iloc[-1]['In-Punch']) and pd.notnull(employee_records.iloc[-1]['Out-Punch']):
            st.write("You have already punched out today")

    def main():
        if 'user_type' not in st.session_state:
            login_page()
        elif st.session_state.user_type == "Owner":
            owner_page()
        elif st.session_state.user_type == "Employee":
            employee_page()

    if __name__ == "__main__":
        main()
