"""
AI-CallConnect Project Overview
Author: Madhurima Rawat

Objective:
AI-CallConnect is an AI-driven voice interaction system designed to handle cold calls,
interpret user inputs, and provide responses. It utilizes fuzzy and exact matching algorithms, 
real-time voice-to-text conversion, and text-to-speech functionality.

Key Features:
- Data Preprocessing: Uses a cleaned dataset to match user queries.
- Fuzzy & Exact Matching: Implements fuzzy matching for more accurate question-answering.
- Voice Integration: Converts user speech to text and response text to speech.
- Real-Time Interaction: Offers dynamic voice-based interaction through Streamlit.

Technologies Used:
- Libraries: pandas, fuzzywuzzy, streamlit, gTTS, pygame, speech_recognition, pyttsx3, etc.
- Matching Algorithms: FuzzyWuzzy for fuzzy matching, exact string matching for precise matches.
- Voice Processing: gTTS and pyttsx3 for text-to-speech, speech_recognition for speech-to-text.
- Data Storage: CSV-based question-answer pairs for storing interactions.

This project aims to provide an intuitive voice interface for interactive cold calling and customer engagement.
"""

# pandas: A powerful data manipulation and analysis library for Python, providing data structures like DataFrames for easy handling of data.
import pandas as pd

# fuzzywuzzy: A library for string matching and comparison, utilizing Levenshtein Distance to calculate differences between sequences.
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

# streamlit: An open-source app framework for building interactive web applications in Python with minimal effort.
import streamlit as st

# gTTS: Google Text-to-Speech (gTTS) is a Python library and CLI tool to convert text into speech using Google's TTS API.
from gtts import gTTS

# os: A Python module that provides a way of interacting with the operating system, including file and directory manipulation.
import os

# uuid: A library used to generate universally unique identifiers (UUIDs) for creating unique IDs in applications.
import uuid

# speech_recognition: A library for performing speech recognition, converting audio to text using various speech recognition engines.
import speech_recognition as sr

# random: A Python library used to generate pseudo-random numbers and make random selections, commonly used for simulations and games.
import random

# base64: A Python module used for encoding and decoding data in a format that is safe to use in URLs and filenames.
import base64

# Setting the page title
# This title will only be visible when running the app locally.
# In the deployed app, the title will be displayed as "Title - Streamlit," where "Title" is the one we provide.
# If we don't set the title, it will default to "Streamlit"
st.set_page_config(
    page_title="AI-CallConnect",
    page_icon="images/Logo.webp",
)


# Function to include background image and opacity
def display_background_image(url, opacity):
    """
    Displays a background image with a specified opacity on the web app using CSS.

    Args:
    - url (str): URL of the background image.
    - opacity (float): Opacity level of the background image.
    """
    # Set background image using HTML and CSS
    st.markdown(
        f"""
        <style>
            body {{
                background: url('{url}') no-repeat center center fixed;
                background-size: cover;
                opacity: {opacity};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# Fallback messages for no match
FALLBACK_MESSAGES = [
    "How can I help you?",
    "Please ask me something else.",
    "I'm here to assist you.",
    "Can I help with anything?",
    "Ask any question you have.",
    "Feel free to ask me anything.",
    "I'm ready to answer your questions.",
    "What do you want to know?",
    "Need any assistance?",
    "Go ahead, I'm listening.",
]


# Function to speak text and play it automatically
def speak_text(text):
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    try:
        # Generate TTS audio
        tts = gTTS(text=text, lang="en")
        tts.save(filename)

        # Embed audio as HTML with autoplay enabled
        audio_html = f"""
        <audio autoplay style="display:none">
            <source src="data:audio/mpeg;base64,{encode_audio(filename)}" type="audio/mpeg">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error during text-to-speech: {e}")

    finally:
        # Ensure the temporary file is deleted
        if os.path.exists(filename):
            os.remove(filename)


# Helper function to encode audio file to base64
def encode_audio(file_path):
    import base64

    with open(file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
        return base64.b64encode(audio_bytes).decode()


# Function to load the CSV file
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File not found at {file_path}")
        return None


# Function to find the best match using exact or fuzzy matching
def find_answer(data, user_question):
    # Exact match search
    exact_match = data[
        data["Question"].str.contains(user_question, case=False, na=False)
    ]
    if not exact_match.empty:
        return exact_match["Answer"].iloc[0]

    # Fuzzy matching
    questions = data["Question"].tolist()
    best_match = process.extractOne(user_question, questions, scorer=fuzz.ratio)

    if best_match and best_match[1] > 70:  # Ensure a valid match with a score threshold
        matched_question = best_match[0]
        matched_row = data[data["Question"] == matched_question]
        return matched_row["Answer"].iloc[0]

    # Fuzzy matching with fallback messages
    best_fallback = process.extractOne(
        user_question, FALLBACK_MESSAGES, scorer=fuzz.ratio
    )
    if best_fallback and best_fallback[1] > 70:
        return best_fallback[0]

    # Return a random fallback message
    return random.choice(FALLBACK_MESSAGES)


# Function to take voice input from the user
def take_voice_input():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    st.write("Listening for your question... Please speak now.")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            user_question = recognizer.recognize_google(audio)
            return user_question
        except sr.WaitTimeoutError:
            return "No input detected."
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.RequestError:
            return "Unable to connect to the recognition service."


# Streamlit UI Homepage
def display_home_page():
    # Use Streamlit session state to track if the greeting has been spoken
    if "greeting_spoken" not in st.session_state:
        st.session_state.greeting_spoken = False

    # Greeting text
    greeting = (
        "Welcome to AI Call Connect. "
        "Our motto is Connecting Conversations, Driving Results. "
        "Your assistant is here to help. "
        "Ask any question, and I will provide an appropriate response."
    )

    st.write("Our motto is Connecting Conversations, Driving Results.")
    st.write("Your assistant is here to help.")
    st.write("Ask any question, and I will provide an appropriate response.")

    # Display the greeting and speak it only if it hasn't been spoken
    if not st.session_state.greeting_spoken:
        speak_text(greeting)
        # Mark greeting as spoken so it won't be spoken again
        st.session_state.greeting_spoken = True

    # Load the data
    file_path = "data/final/question_answer.csv"
    data = load_data(file_path)

    if data is not None and not data.empty:
        # Take voice input from the user
        if st.button("Speak Now"):
            user_question = take_voice_input()
            st.write(f"**You Asked:** {user_question}")

            if user_question:
                answer = find_answer(data, user_question)
                st.write(f"**Response:** {answer}")
                speak_text(answer)
    else:
        st.error("No data available to process your questions.")


def display_project_description():

    image_path_logo = "images/Logo.webp"

    # Read the image and encode it in base64
    with open(image_path_logo, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()

    # Construct the URL for the background image
    img_url_logo = f"data:image/png;base64,{encoded_string}"

    image_path_architecture = "images/System_Architecture.png"

    # Read the image and encode it in base64
    with open(image_path_architecture, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()

    # Construct the URL for the background image
    img_url_architecture = f"data:image/png;base64,{encoded_string}"

    st.markdown(
        f"""
    <h3 style="text-align: center;">Connecting Conversations, Driving Results</h3>
    <p><strong>AI-Call Connect</strong> is a project aimed at building an intelligent phone agent capable of making cold calls to specific types of customers and holding meaningful conversations. The agent leverages advanced AI techniques to interpret user inputs, process them, and respond intelligently through voice output.</p>

    <img src="{img_url_logo}" style="height: 100px; display: block; margin: 0 auto;">

    <br>
    <br>
    
    <p>This project was developed as part of <strong><a href="https://unstop.com/hackathons/encode-2025-code-to-innovate-udgam-2025-iit-guwahati-1289240" target="_blank">EnCode 2025 - Code to Innovate</a></strong>, a hackathon organized by the Indian Institute of Technology (IIT), Guwahati.</p>
    <p>The core objective is to develop a seamless AI-driven voice interaction system. Our approach combines dialogue dataset preprocessing, fuzzy and exact matching algorithms, and real-time voice-to-text and text-to-voice conversion to enhance conversational capabilities.</p>

    <h4>Methodology</h4>
    
     <img src="{img_url_architecture}" style="height: 200px; display: block; margin: 0 auto;">
     <br>
     
    <ol>
        <li><strong>Data Preprocessing</strong>: We utilized the Switchboard Dialog Dataset, cleaned and preprocessed the data, and converted it into a question-answer format.</li>
        <li><strong>Matching Algorithms</strong>: Using both fuzzy and exact matching techniques, the system processes user inputs and identifies the most relevant responses.</li>
        <li><strong>Voice Integration</strong>: Real-time voice-to-text conversion interprets user inputs, and the system converts processed responses back into voice output.</li>
        <li><strong>Machine Learning</strong>: We experimented with advanced models such as LSTM and Transformers to improve the accuracy of matching and dialogue prediction.</li>
        <li><strong>Collaboration</strong>: The project is collaboratively developed and managed through GitHub, ensuring effective teamwork and version control.</li>
    </ol>

    <h3>Tools Used</h3>
   <ol>
        <li><strong>NLP Libraries</strong>: NLTK for dialogue preprocessing and matching.</li>
        <li><strong>Fuzzy Matching & Exact Matching</strong>: Techniques for identifying approximate and exact text matches.</li>
        <li><strong>Pandas</strong>: Used for data analysis and manipulation.</li>
        <li><strong>Streamlit</strong>: Utilized for developing and deploying interactive web applications.</li>
        <li><strong>GitHub</strong>: Facilitates collaboration and version control within the team.</li>
    </ol>

    """,
        unsafe_allow_html=True,
    )


# Function to display team members' contact information in a column-wise format
def display_contact_information():

    # Define team member information with updated descriptions
    team_members = [
        {
            "Name": "Madhurima Rawat",
            "Role": "Project Planner & Developer",
            "Responsibilities": "Responsible for project planning, managing the GitHub repository, code documentation, voice processing, deploying on Streamlit, and preprocessing and visualizing data.",
            "Tools": "GitHub, PyGame, Streamlit, Python, Pandas",
            "GitHub": '<a href="https://github.com/madhurimarawat" target="_blank">GitHub</a>',
            "LinkedIn": '<a href="https://www.linkedin.com/in/madhurima-rawat/" target="_blank">LinkedIn</a>',
            "Email": '<a href="mailto:rawtamadhurima@gmail.com" target="_blank">Email</a>',
        },
        {
            "Name": "Geetanshu Dev Meshram",
            "Role": "Data Analyst",
            "Responsibilities": "Focused on voice processing, data cleaning, and generating artificial datasets.",
            "Tools": "Python, Machine Learning libraries",
            "GitHub": '<a href="https://github.com/geetanshudev" target="_blank">GitHub</a>',
            "LinkedIn": '<a href="https://www.linkedin.com/in/geetanshu-dev-meshram-2b3b61240/" target="_blank">LinkedIn</a>',
            "Email": '<a href="mailto:meshramgeetanshudev@gmail.com" target="_blank">Email</a>',
        },
        {
            "Name": "Sneha Jha",
            "Role": "Data Analyst",
            "Responsibilities": "Specialized in processing text data, natural language processing (NLP), and generating artificial datasets.",
            "Tools": "NLP libraries, Machine Learning libraries, Pandas",
            "GitHub": '<a href="https://github.com/Sneha100802" target="_blank">GitHub</a>',
            "LinkedIn": '<a href="https://www.linkedin.com/in/sneha-jha-808796261/" target="_blank">LinkedIn</a>',
            "Email": '<a href="mailto:jhasneha344@gmail.com" target="_blank">Email</a>',
        },
    ]

    # Display a brief summary of the team with names, LinkedIn profiles, and a description
    st.markdown("### Team Overview")
    st.markdown(
        "Our team consists of three passionate individuals who bring diverse skills to the table. "
        "We are focused on developing cutting-edge solutions in voice data processing, Streamlit app development, and project management. "
        "Each team member plays a critical role in the success of the project, and we are excited to share our expertise and dedication."
    )

    # Explicitly written details for each team member with LinkedIn links
    st.markdown(
        "[Madhurima Rawat](https://www.linkedin.com/in/madhurima-rawat/) : &nbsp; Project Planner & Developer specialized in project planning, managing GitHub repository, code documentation, Streamlit deployment, data visualization, and preprocessing of numerical and voice data. Tools: GitHub, Streamlit, Python, Pandas"
    )
    st.markdown(
        "[Geetanshu Dev Meshram](https://www.linkedin.com/in/geetanshu-dev-meshram-2b3b61240/) : &nbsp; Voice Processing Specialist & Backend Developer specializing in voice data processing, data cleaning, and generating artificial datasets for model building. Tools: Python, Machine Learning libraries"
    )
    st.markdown(
        "[Sneha Jha](https://www.linkedin.com/in/sneha-jha-808796261/) : &nbsp; NLP Specialist & Model Developer specialized in processing text data, natural language processing (NLP), and developing hybrid models for artificial dataset generation. Tools: NLP libraries, Machine Learning libraries, Pandas"
    )

    st.markdown("---")

    # HTML Table with centered content and reduced width
    html_table = f"""
    <table style="width: 80%; border: 1px solid black; border-collapse: collapse; margin-left: auto; margin-right: auto;">
        <tr>
            <th style="padding: 8px; text-align: center;"><i class="fas fa-id-card"></i> &nbsp; Name</th>
            <th style="padding: 8px; text-align: center;">Madhurima Rawat</th>
            <th style="padding: 8px; text-align: center;">Geetanshu Dev Meshram</th>
            <th style="padding: 8px; text-align: center;">Sneha Jha</th>
        </tr>
        <tr>
            <td style="padding: 8px; text-align: center;"><i class="fas fa-user-tie"></i> &nbsp; <strong>Role</strong></td>
            <td style="padding: 8px; text-align: center;">{team_members[0]['Role']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[1]['Role']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[2]['Role']}</td>
        </tr>
        <tr>
            <td style="padding: 8px; text-align: center;"><i class="fas fa-tasks"></i> &nbsp; <strong>Responsibilities</strong></td>
            <td style="padding: 8px; text-align: center;">{team_members[0]['Responsibilities']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[1]['Responsibilities']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[2]['Responsibilities']}</td>
        </tr>
        <tr>
            <td style="padding: 8px; text-align: center;"><i class="fas fa-tools"></i> &nbsp; <strong>Tools</strong></td>
            <td style="padding: 8px; text-align: center;">{team_members[0]['Tools']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[1]['Tools']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[2]['Tools']}</td>
        </tr>
        <tr>
            <td style="padding: 8px; text-align: center;"><i class="fab fa-github"></i> &nbsp;<strong>GitHub</strong></td>
            <td style="padding: 8px; text-align: center;">{team_members[0]['GitHub']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[1]['GitHub']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[2]['GitHub']}</td>
        </tr>
        <tr>
            <td style="padding: 8px; text-align: center;"><i class="fab fa-linkedin"></i> &nbsp;<strong>LinkedIn</strong></td>
            <td style="padding: 8px; text-align: center;">{team_members[0]['LinkedIn']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[1]['LinkedIn']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[2]['LinkedIn']}</td>
        </tr>
        <tr>
            <td style="padding: 8px; text-align: center;"><i class="fas fa-envelope"></i> &nbsp;<strong>Email</strong></td>
            <td style="padding: 8px; text-align: center;">{team_members[0]['Email']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[1]['Email']}</td>
            <td style="padding: 8px; text-align: center;">{team_members[2]['Email']}</td>
        </tr>
    </table>
    """

    # Render the table
    st.markdown(html_table, unsafe_allow_html=True)


# Function to display resources information
def display_resources_information():
    st.markdown("### Resources and Links")

    # Resources section
    st.markdown(
        """
        **Switchboard Dialog Dataset:**
        - [Access the GitHub Repository for Data Download](https://github.com/cgpotts/swda)
        
        **Illustrations and Logo:**
        - [Project Logo (Created with GPT)](https://chatgpt.com/)
        - [Streamlit App Background Image (Designed using GPT)](https://chatgpt.com/)
        """
    )


# Main code to initialize Streamlit
if __name__ == "__main__":

    # Title
    st.title("Welcome to AI-CallConnect")

    # Display background with local image
    display_background_image(
        "https://github.com/madhurimarawat/AI-CallConnect/raw/main/Codes/images/Illustration.webp",  # Local image path
        0.8,  # Opacity level
    )

    # Sidebar navigation for different sections
    st.sidebar.title("Explore")
    selected_section = st.sidebar.radio(
        "Go to",
        [
            "Connect Now",
            "Project Description",
            "Meet the Team",
            "Resources",
        ],
    )

    if selected_section == "Connect Now":
        display_home_page()

    elif selected_section == "Project Description":
        """
        Gives a concise description of the project objectives,
        methodology, and expected outcomes.
        """
        display_project_description()

    elif selected_section == "Meet the Team":
        """
        Introduces the team members working on the project and provides
        their contact information.
        """
        display_contact_information()

    elif selected_section == "Resources":
        """
        Lists resources and links relevant to the project, including stock data
        sources and illustrations.
        """
        display_resources_information()

    # Using Font Awesome icons for links
    st.sidebar.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <a href="https://github.com/madhurimarawat/AI-CallConnect" target="_blank"><i class="fab fa-github"> &nbsp;</i> GitHub Repository</a> &nbsp;
        """,
        unsafe_allow_html=True,
    )
