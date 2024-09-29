import streamlit as st
import duckdb
import pandas as pd
from groq import Groq
from datetime import date


# Initialize DuckDB connection
conn = duckdb.connect('users.db')

# Create a users table if not exists (email is no longer a primary key)
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email STRING,
        name STRING,
        age INTEGER,
        town STRING,
        state STRING,
        weight FLOAT,
        height FLOAT,
        gender STRING,
        goal STRING,
        prompt STRING,
        workout STRING,
        date_added STRING
    )
''')

def create_workout(prompt):
    workout_app_key = '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'
    client = Groq(
    api_key=workout_app_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""you are my personal trainer at my gym..give me 10 exercises a {prompt} at home or at the gym... be clear about what excercises i should do
                            some helpful information is that i have access to machines at planetfitness""",
            }
        ],
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content

# Function to insert user data into the database
def add_user(email, name, age, town, state, weight, height, gender, goal, prompt, workout):
    today = date.today()

    conn.execute(
        "INSERT INTO users (email, name, age, town, state, weight, height, gender, goal, prompt, workout, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (email, name, age, town, state, weight, height, gender, goal, prompt, workout, today.strftime("%Y-%m-%d"))
    )

# Cool style for the app
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Lets create your workout!</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Fill in your details below:</h3>", unsafe_allow_html=True)

# User input form
with st.form("user_form"):
    email = st.text_input("Email")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=120, value=25)
    town = st.text_input("City")
    state = st.text_input("State")
    weight = st.number_input("Weight (lbs)", min_value=1.0, value=70.0)
    height = st.number_input("Height (inches)", min_value=50.0, value=170.0)
    gender = st.selectbox("Gender", ["Male", "Female"])
    goal = st.selectbox("Goal", ["Loose Weight", "Gain Muscle", "Tone Muscles"])
    # cadence = st.selectbox("Cadence", ["Daily", "Weekly"])

    submit_button = st.form_submit_button("Generate my workout")

# Handle form submission
if submit_button:
    
    # st.success(f"User '{name}' added successfully!")
    prompt=f"""{gender} that is {height} tall and {weight} lbs and I want to {goal}"""
    workout = create_workout(prompt = prompt)
    st.text(f"""Hi {name}, here is your workout:\n {workout}""")
    add_user(email, name, age, town, state, weight, height, gender, goal, prompt, workout)
    st.success(f""" Workout added successfully for {email}""")
    

# Optional: Show existing users in the database
if st.checkbox("Show existing users"):
    users_df = conn.execute("SELECT email, date_added, workout FROM users order by date_added desc ").df()
    st.dataframe(users_df)
