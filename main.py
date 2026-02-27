import speech_recognition as sr
import pyttsx3
from config import SYSTEM_PROMPT
from openai import OpenAI
import datetime
import sys
from safety_filter import is_safe

# =====================================
# SCHOOL & ASSISTANT CONFIGURATION
# =====================================

SCHOOL_NAME = "Kerala Model High School"
ASSISTANT_NAME = "Aarya"
PRINCIPAL = "Siju S Nair"
VICE_PRINCIPAL = "Smitha S Nair"

# =====================================
# OPENROUTER CLIENT SETUP
# =====================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

# =====================================
# TEXT TO SPEECH SETUP
# =====================================

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 140)
engine.setProperty('volume', 1.0)

def speak(text):
    print(f"{ASSISTANT_NAME}:", text)
    engine.say(text)
    engine.runAndWait()

# =====================================
# MEMORY STORAGE
# =====================================

conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

last_academic_question = None

# =====================================
# SPEECH RECOGNITION
# =====================================

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except:
        return None

# =====================================
# GREETING HANDLER
# =====================================

def handle_greetings(text):
    if "good morning" in text:
        return f"Good morning. I am {ASSISTANT_NAME}, the academic assistant of {SCHOOL_NAME}. How may I assist you today?"
    elif "good afternoon" in text:
        return f"Good afternoon. I am {ASSISTANT_NAME}. How can I help you?"
    elif "good evening" in text:
        return f"Good evening. I am {ASSISTANT_NAME}. I am here to assist you."
    elif "hello" in text or "hi" in text:
        return f"Hello. I am {ASSISTANT_NAME}, the academic assistant of {SCHOOL_NAME}. How may I help you?"
    return None

# =====================================
# AI RESPONSE FUNCTION WITH MEMORY
# =====================================

def ask_aarya(question):

    global conversation_history

    conversation_history.append({"role": "user", "content": question})

    # Keep memory small (last 6 messages only)
    if len(conversation_history) > 7:
        conversation_history = [conversation_history[0]] + conversation_history[-6:]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        max_tokens=350,
        temperature=0.5
    )

    answer = response.choices[0].message.content

    conversation_history.append({"role": "assistant", "content": answer})

    return answer

# =====================================
# MAIN PROGRAM
# =====================================

def main():
    global last_academic_question

    speak(f"Hello, I am {ASSISTANT_NAME}. Welcome to {SCHOOL_NAME}. How can I assist you today?")

    while True:
        question = listen()

        if question is None:
            continue

        print("You said:", question)
        question_lower = question.lower()

        # ================= EXIT =================
        if any(word in question_lower for word in ["exit", "quit", "stop", "bye", "thank you", "end"]):
            speak(f"Thank you for using {ASSISTANT_NAME}. Have a wonderful day.")
            sys.exit()

        # ================= GREETINGS =================
        greeting_reply = handle_greetings(question_lower)
        if greeting_reply:
            speak(greeting_reply)
            continue

        # ================= SCHOOL INFO =================
        if "principal" in question_lower:
            speak(f"The Principal of {SCHOOL_NAME} is {PRINCIPAL}.")
            continue

        if "vice principal" in question_lower:
            speak(f"The Vice Principal of {SCHOOL_NAME} is {VICE_PRINCIPAL}.")
            continue

        if "who are you" in question_lower:
            speak(f"I am {ASSISTANT_NAME}. I am here to assist you.")
            continue

        if "how are you" in question_lower:
            speak("I am Doing Great. How may i assist you.")
            continue

        if "hu r u" in question_lower:
            speak("I am Doing Great. How may i assist you.")
            continue

        # ================= TIME =================
        if "time" in question_lower:
            now = datetime.datetime.now()
            speak(f"The current time is {now.strftime('%I:%M %p')}.")
            continue

        # ================= DATE =================
        if "date" in question_lower or "today" in question_lower:
            today = datetime.date.today()
            speak(f"Today is {today.strftime('%A, %d %B %Y')}.")
            continue

        # ================= CONTINUE FEATURE =================
        if any(word in question_lower for word in ["continue", "continue explaining", "tell more", "explain more"]):
            if last_academic_question:
                follow_up = f"Continue explaining about {last_academic_question} in more detail."
                answer = ask_aarya(follow_up)
                speak(answer)
            else:
                speak("There is no previous topic to continue.")
            continue

        # ================= SAFETY FILTER =================
        if not is_safe(question):
            speak(f"I am {ASSISTANT_NAME}, designed only for academic and school-related assistance.")
            continue

        # ================= DEFAULT AI RESPONSE =================
        last_academic_question = question
        answer = ask_aarya(question)
        speak(answer)


if __name__ == "__main__":
    main()