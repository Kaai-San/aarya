
restricted_words = ["violence", "kill", "abuse", "adult", "18+", "sex", "porn"]

def is_safe(text):
    for word in restricted_words:
        if word.lower() in text.lower():
            return False
    return True
