from nltk import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer  
from nltk.corpus import stopwords   
import json
import re
import spacy
# Initialization of objects that don't need to be recreated each time
stop_words = stopwords.words('english')

sent_analyzer = SentimentIntensityAnalyzer()  # Sentiment analysis instance

nlp = spacy.load('en_core_web_md')
# Global DataFrame (for the purpose of this example)
df = 'temp'



# Function to get sentiment score for text
def get_sentiment(text):
    score = sent_analyzer.polarity_scores(text)['compound']
    if score < 0:
        return "Negative"
    elif score > 0:
        return "Positive"
    else:
        return "Neutral"

def clean_with_timestamp(comment):

    comment = comment.lower()
    if ('<a' in comment) and ('</a>' in comment):
        timestamp_pattern = r'<a[^>]*>(\d{1,2}:\d{2})</a>'

        # Extract the timestamp
        timestamp = re.search(timestamp_pattern, comment)

        if timestamp:
            timestamp = timestamp.group(1)

            # Regular expression to remove the <a> tag itself
            cleaned_comment = re.sub(r'<a[^>]*>.*?</a>', '', comment).strip()

            # Combine the timestamp with the rest of the comment text
            final_comment = f"{cleaned_comment} {timestamp}".strip()
        else:
            final_comment = comment  # No timestamp found, return comment as is

        return final_comment
    else:
        return comment


# Function to preprocess text by tokenizing and removing stopwords
def preprocess_text(text):
    # Regex to identify and preserve timestamps (e.g., 0:21, 12:45)
    
    timestamp_pattern = r'\b\d{1,2}:\d{2}\b'
    
    # Find all timestamps in the text
    timestamps = re.findall(timestamp_pattern, text)

    # Replace timestamps with placeholders
    for idx, timestamp in enumerate(timestamps):
        text = text.replace(timestamp, f'__TIMESTAMP_{idx}__')

    # Tokenize the text
    doc = nlp(text.lower()) 

    
    
    # Remove stopwords and non-alphanumeric tokens, but preserve placeholders
    tokens = [word.lemma_ for word in doc if word.text not in stop_words and (word.text.isalnum() or 'TIMESTAMP' in word.text)]
    
    # Restore timestamps by replacing placeholders with actual timestamps
    for idx, timestamp in enumerate(timestamps):
        tokens = [timestamp if token == f'__TIMESTAMP_{idx}__' else token for token in tokens]

    return tokens


# Function to print topics from a JSON response
def print_topics(x):
    response_dict = json.loads(x)
    result = ''
    for topic, details in response_dict.items():
        result += f"<h3>{topic}:</h3>"
        result += f"<p><b>Keywords:</b> {details['Keywords']}</p>" 
        result += f"<p><b>Interpretation:</b> {details['Interpretation']}</p>"
        result += "<p>-------------------------------------</p>"
    return result

# Function to generate summary of sentiment in the DataFrame
def generate_summary(df):
    total_comments = len(df)
    positive_comments = len(df[df['sentiment'] == 'Positive'])
    negative_comments = len(df[df['sentiment'] == 'Negative'])
    neutral_comments = len(df[df['sentiment'] == 'Neutral'])
    common_emotion = df['sentiment'].value_counts().idxmax()

    summary = f"""Out of {total_comments} comments:\n
- **{positive_comments}**  are positive\n
- **{neutral_comments}**  are  neutral\n
- **{negative_comments}** are  negative\n 
The most common emotion expressed is **'{common_emotion}'**."""
    return summary

