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
    workout_app_key = st.secrets["workout_app_key"] 
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

# User input form with grid layout
with st.form("user_form"):
    # Create a two-column layout for name, email, and location
    col1, col2 = st.columns(2)
    
    with col1:
        email = st.text_input("Email", value="givememyworkout@example.com")  # Preset email
        name = st.text_input("Name", value="gimmemy workout")  # Preset name
        town = st.text_input("City", value="gainsville") 
    
    with col2:
        state = st.text_input("State", value = "Musclechusetts")
        gender = st.selectbox("Gender", ["Male", "Female"])
        goal = st.selectbox("Goal", ["Best workout ever", "Gain Muscle","Lose Weight", "Tone Muscles"])
    
    # Create a three-column layout for sliders (age, weight, height)
    col3, col4, col5 = st.columns(3)
    
    with col3:
        age = st.slider("Age", min_value=1, max_value=120, value=25)
    
    with col4:
        weight = st.slider("Weight (lbs)", min_value=1.0, max_value=400.0, value=175.0)
    
    with col5:
        height = st.slider("Height (inches)", min_value=50.0, max_value=96.0, value=72.0)
    
    # Submit button
    submit_button = st.form_submit_button("Generate my workout")


# Handle form submission
if submit_button:
    

    # Check if the current month is December, January, or February
    if date.today().month in [11, 12, 1, 2]:
        st.snow()  
    else:
        st.balloons()
    
    # Generate workout prompt
    prompt = f"{gender} that is {height} tall and {weight} lbs and I want to {goal}"
    workout = create_workout(prompt=prompt)
    
    # Pop-out modal to read the full workout using an expander
    with st.expander(f"Hi {name}, click to see your workout"):
        st.text(workout)
    
    # Add user info to the database
    add_user(email, name, age, town, state, weight, height, gender, goal, prompt, workout)
    
    # Show success message with confetti
    st.success(f"Workout added successfully for {email}")


# Input to show existing users in the database
search_email = st.text_input(f"Enter your email to view past workouts", value = f"{email}")

# Show past workouts if an email is provided
if search_email:
    query = """
        SELECT 
            substr(email, 1, 3) || '***********' AS masked_email,
            date_added,
            goal,
            workout
        FROM users
        WHERE email LIKE ?
        ORDER BY date_added DESC
    """
    
    # Add wildcards to the email parameter in the Python code
    users_df = pd.read_sql_query(query, conn, params=[f'%{search_email}%'])
    
    if not users_df.empty:
        st.dataframe(users_df)
    else:
        st.warning(f"No past workouts found for {search_email}")
