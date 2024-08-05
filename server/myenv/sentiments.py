import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Path to your CSV file
csv_file_path = 'clean_transcript.csv'

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)
# Sample transcript



def get_encouragement(dataframe):
    
    positive_words = [
        "achievement", "amazing", "appreciate", "awesome", "beautiful", 
        "brilliant", "celebrate", "champion", "cheerful", "confident", 
        "courageous", "creative", "delight", "determined", "empower", 
        "encourage", "enthusiastic", "excellence", "fantastic", "friendly", 
        "generous", "grateful", "happy", "hopeful", "incredible", 
        "inspiring", "joyful", "kind", "lovely", "motivated", 
        "optimistic", "outstanding", "passionate", "positive", "remarkable", 
        "resilient", "spectacular", "strong", "supportive", "talented", 
        "terrific", "thriving", "trustworthy", "unstoppable", "valiant", 
        "vibrant", "wonderful", "zealous", "good", "great", "believe", 
        "excellent", "superb", "impressive", "marvelous", "exceptional", 
        "splendid", "nice", "progress", "striving", "close", "job", 
        "fire", "rocking", "mastering"
    ]


    def preprocess_text(text):
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalpha()]
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        return tokens

    def calculate_encouragement_score(tokens, encouragement_words):
        score = 0
        words = []


        for token in tokens:
            if token in encouragement_words:
                score += 1
                words.append(token)
        return score, words

    teacher_df = df[df['Role'] == 'teacher']
    text_data = teacher_df['Text'].tolist()
    article_text = ""

    for text in text_data:
        article_text += str(text) + " "

    tokens = preprocess_text(article_text)
    score, words = calculate_encouragement_score(tokens, positive_words)
    return score, words




    
    encouragement_words = ["fantastic", "good", "great", "believe", "don't give up", "you can do it", "keep up"]

    def preprocess_text(text):
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalpha()]
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        return tokens

    def calculate_encouragement_score(tokens, encouragement_words):
        score = 0
        for word in tokens:
            if word in encouragement_words:
                score += 1
        return score

    text_data = dataframe['Text'].tolist()
    article_text = ""

    for text in text_data:
        article_text += str(text) + " "

    tokens = preprocess_text(article_text)
    score = calculate_encouragement_score(tokens, encouragement_words)
    return score
    # return tokens
print(f"Encouraging words: {get_encouragement(df)[0]}")

