import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from openai import OpenAI
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import math

def clean(file):

    def read(file):
        timestamps = []
        speakers = []
        texts = []
        roles = []
        times = []

        def extract_time(timestamp):

            def time_to_seconds_helper(time_str):
                """
                Converts a time string in the format HH:MM:SS.mmm to seconds.
                """
                hours, minutes, seconds = time_str.split(':')
                seconds, milliseconds = seconds.split('.')
                total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
                return total_seconds
        
            start_time_str, end_time_str = timestamp.split(' --> ')
            start_time_seconds = time_to_seconds_helper(start_time_str)
            end_time_seconds = time_to_seconds_helper(end_time_str)
            
            duration = round(end_time_seconds - start_time_seconds, 2)
            return duration



        lines = file.readlines()
        lines = lines[2:]
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if i % 4 == 1:
                timestamps.append(line)
                times.append(extract_time(line))
            elif i % 4 == 2:
                try:
                    name, text = line.rsplit(': ', 1)
                    speakers.append(name)
                    texts.append(text)
                    # Extract role from name
                    if "Teacher" in name:
                        roles.append("teacher")
                    elif "Champ" in name:
                        roles.append("champ")
                    else:
                        roles.append("unknown")
                except ValueError:
                    # If splitting fails, remove the last added timestamp
                    if timestamps:
                        timestamps.pop()
                        times.pop()
                    i += 1  # Skip the next line
            
            i += 1

        return timestamps, speakers, texts, roles, times

    timestamps, speakers, texts, roles, times = read(file)
    data = {'Timestamp': timestamps, 'Times': times, 'Speaker': speakers, 'Role': roles, 'Text': texts}
    df = pd.DataFrame(data)
    df.to_csv('clean_transcript.csv', index=False)
    return df

def get_summary(dataframe):
        
    def find_speaking_times(dataframe):
        # Step 2: Calculate total speaking times
        total_time = dataframe['Times'].sum()
        teacher_time = dataframe[dataframe['Role'] == 'teacher']['Times'].sum()
        champ_time = dataframe[dataframe['Role'] == 'champ']['Times'].sum()

        # Step 3: Compute percentages
        teacher_percentage = round((teacher_time / total_time) * 100)
        champ_percentage = round((champ_time / total_time) * 100)

        return teacher_percentage, champ_percentage

    def find_bad_words(dataframe):

        bad_words = ['Arsehole', 'Asshat', 'Asshole', 'Bastard', 'Bloody', 'Blowjob', 'Bollocks', 'Bugger', 'Bullshit', 
                    'Clusterfuck', 'Cock', 'Cocksucker', 'Cornhole', 'Cunt', 'Damn', 'Dick', 'Faggot', 'Feck', 'Fuck', 
                    'Motherfucker', 'Nigga', 'Nigger', 'Prick', 'Pussy', 'Shit', 'Slut', 'Wanker', 'Whore']
        
        bad_words_df = dataframe[
            (dataframe['Role'] == 'teacher') & 
            (dataframe['Text'].str.contains('|'.join(bad_words), case=False))
        ]
        
        # If bad words are found, return the timestamps and words
        if not bad_words_df.empty:
            result = bad_words_df[['Timestamp', 'Text']]
            return_list = []
            for _, row in result.iterrows():
                timestamp = row['Timestamp'][:8]  # Get only the first 8 characters
                return_list.append(f"{timestamp}: {row['Text']}")
            return "\n".join(return_list)
        else:
            return "none"
        
    def find_sentiments(dataframe):

        def sentiment_scores_helper(text):
            obj = SentimentIntensityAnalyzer()
            sentiment_dict = obj.polarity_scores(text)
            return 100*(1/(1+pow(math.e,(10*sentiment_dict["compound"]))))
        
        # Ensure all text entries are strings
        dataframe['Text'] = dataframe['Text'].astype(str)
        
        # Apply the sentiment_scores function to each text entry
        dataframe['Sentiment'] = dataframe['Text'].apply(sentiment_scores_helper)
        
        # Separate sentiments for teacher and champ
        teacher_sentiments = dataframe[dataframe['Role'] == 'teacher']['Sentiment']
        champ_sentiments = dataframe[dataframe['Role'] == 'champ']['Sentiment']
        
        # Calculate average sentiment scores
        avg_teacher_sentiment = teacher_sentiments.mean()
        avg_champ_sentiment = champ_sentiments.mean()
        
        return round(avg_teacher_sentiment, 1), round(avg_champ_sentiment, 1)

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

        teacher_df = dataframe[dataframe['Role'] == 'teacher']
        text_data = teacher_df['Text'].tolist()
        article_text = ""

        for text in text_data:
            article_text += str(text) + " "

        tokens = preprocess_text(article_text)
        score, words = calculate_encouragement_score(tokens, positive_words)
        return score, words

    def get_summarized_text(dataframe):

        text_data = dataframe['Text'].tolist()
        article_text = ""
        
        for text in text_data:
            article_text += str(text) + " "

        client = OpenAI()
        get_summary = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a tutoring lesson summarizer. Ordered list 5 topics from the lesson content while ignoring irrelavent text."},
            {"role": "user", "content": article_text}
        ]
        )
        return get_summary.choices[0].message.content

    dataframe['Text'] = dataframe['Text'].astype(str)
    return {
        "speaking_percents": find_speaking_times(dataframe),
        "bad_words": find_bad_words(dataframe),
        "sentiments": find_sentiments(dataframe),
        "summarized_text": get_summarized_text(dataframe),
        "encouragement": get_encouragement(dataframe),
    }

def both(file):
    dataframe = clean(file)
    return get_summary(dataframe)
    # summary_string  = f"Speaking times:                T: {summary['speaking_percents'][0]}% "
    # summary_string += f"S: {summary['speaking_percents'][1]}%\n"
    # summary_string += f"Bad words said by teacher:        {summary['bad_words']}\n"
    # summary_string += f"Positive language (-10 to 10): T: {summary['sentiments'][0]} "
    # summary_string += f"S: {summary['sentiments'][1]}\n"
    # summary_string += f"Encouraging words:                {summary['encouragement'][0]}\n\n"
    # summary_string += f"Lesson content:\n{summary['summarized_text']}"
    
    # return summary_string
