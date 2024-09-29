import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq
from datetime import date

# Initialize SQLite3 connection
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create a users table if not exists (email is no longer a primary key)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT,
        name TEXT,
        age INTEGER,
        town TEXT,
        state TEXT,
        weight REAL,
        height REAL,
        gender TEXT,
        goal TEXT,
        prompt TEXT,
        workout TEXT,
        date_added TEXT
    )
''')
conn.commit()

def create_workout(prompt):
    workout_app_key = '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'
    client = Groq(api_key=workout_app_key)

    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": f"""you are my personal trainer at my gym, but dont introduce yourself... only give me 10 exercises a {prompt} at home or at the gym... 
                           be clear about what exercises I should do, some helpful information is that I have access to machines at Planet Fitness and i plan to workout for an hour""",
        }],
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content

# Function to insert user data into the database
def add_user(email, name, age, town, state, weight, height, gender, goal, prompt, workout):
    today = date.today()

    cursor.execute(
        '''INSERT INTO users (email, name, age, town, state, weight, height, gender, goal, prompt, workout, date_added)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (email, name, age, town, state, weight, height, gender, goal, prompt, workout, today.strftime("%Y-%m-%d"))
    )
    conn.commit()

# Cool style for the app
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Let's create your workout!</h1>", unsafe_allow_html=True)
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
    goal = st.selectbox("Goal", ["Lose Weight", "Gain Muscle", "Tone Muscles"])

    submit_button = st.form_submit_button("Generate my workout")

# Handle form submission
if submit_button:
    prompt = f"{gender} that is {height} tall and {weight} lbs and I want to {goal}"
    workout = create_workout(prompt=prompt)
    st.text(f"Hi {name}, here is your workout:\n{workout}")
    add_user(email, name, age, town, state, weight, height, gender, goal, prompt, workout)
    st.success(f"Workout added successfully for {email}")

# Optional: Show existing users in the database
if st.checkbox(f"Show past workouts for your {email}"):
    users_df = pd.read_sql_query(f"SELECT email, date_added, goal, workout FROM users where email = '{email}' ORDER BY date_added DESC", conn)
    st.dataframe(users_df)
