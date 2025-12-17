import streamlit as st
from gensim import corpora
from gensim.models import LdaModel
import google.generativeai as genai
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from scraping_comments import scraper
from preprocessing_app import clean_with_timestamp,get_sentiment, preprocess_text, print_topics, generate_summary
import requests



if 'show_data' not in st.session_state:
    st.session_state.show_data = True

if 'show_plot' not in st.session_state:
    st.session_state.show_plot = True

if 'show_trend' not in st.session_state:
    st.session_state.show_trend = True



def get_video_info(video_url, api_key):
    """Get the channel name and video title of a YouTube video using the YouTube Data API."""
    video_id = video_url.split('v=')[1]
    if not video_id:
        return "Invalid video URL or ID could not be extracted"
    
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet&key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            # Extract channel name and video title
            channel_name = data['items'][0]['snippet']['channelTitle']
            video_title = data['items'][0]['snippet']['title']
            return {"channel_name": channel_name, "video_title": video_title}
        else:
            return "Video not found"
    else:
        return f"Error: {response.status_code}"

# @st.cache_data
def get_topics(sentiment,num,channel,title,model):
    data = df[['english_comm']].copy()
    sentiment = sentiment.lower()
    # Filter the DataFrame based on the sentiment
    if sentiment.lower() in ('positive','neutral','negative'):
        data = df[df['sentiment'].str.lower().str.contains(sentiment)]

    topic_data = data['english_comm'].apply(preprocess_text).tolist()
    id2word = corpora.Dictionary(topic_data)
    corpus = [id2word.doc2bow(doc) for doc in topic_data]
    
    # alpha_values = ['auto', 0.001, 0.01]
    # coherence_scores = []
    
    # for alpha in alpha_values:
    #     lda_model = LdaModel(corpus=corpus, id2word=id2word, random_state=1, num_topics= num, alpha=alpha, passes=10)
    #     coherence_model = CoherenceModel(model=lda_model, texts=topic_data, dictionary=id2word, coherence='c_v')
    #     coherence_score = coherence_model.get_coherence()
    #     coherence_scores.append((alpha, coherence_score))

    # best_alpha = sorted(coherence_scores, key=lambda x: x[1], reverse=True)[0][0]
    # lda_model = LdaModel(corpus=corpus, id2word=id2word, random_state=1, num_topics= num, alpha=best_alpha, passes=10)

    lda_model = LdaModel(corpus=corpus, id2word=id2word, random_state=1, num_topics= num, alpha='auto', passes=10)

    topics = lda_model.print_topics()
    

    prompt = f"""
Analyze the following topics extracted from YouTube video comments for the channel "{channel}" and video title "{title}". 
You can also set the overall context based on the keywords if possible
Provide interpretations in key-value pairs, directly outputting the results without any introductory or concluding text. 

set context of the interpretations based on:
1. **Real-world facts and current events** 
2. **Specific context of the channel and video title**

desired output format:
    {{"Topic 0":
    {{Keywords: ["keyword 1", "keyword 2", "keyword 3" , ...],
    Interpretation: "..."
    }}, ...}}


**These are the Topics:**
{topics}
"""

    # prompt = f"""I've performed topic modeling on YouTube video comments. channel name : {channel}, video title: {title}. Please interpret the following topics in key-value pairs as the given format. Provide the output directly, without intro or conclusion. Try to interpret the context of comments based on real facts, channel name, video title(not necessary).

    # {{"Topic 0":
    # {{Keywords: ["keyword 1", "keyword 2", "keyword 3" , ...],
    # Interpretation: "..."
    # }}, ...}}

    # Topics:  {topics} """
    response = model.generate_content(prompt)

    x = response.text
    x = x.replace("\n","")
    x = x.replace("`","")
    x = x.replace('json',"")
    return x



def create_countplot():
    fig, ax = plt.subplots()
    sns.countplot(x='sentiment', data=df, ax=ax, order = ['Positive','Neutral','Negative'],legend = False ,hue= 'sentiment',palette={'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'})
    for container in ax.containers:
        ax.bar_label(container, fmt='%d', label_type='edge')  # Display integer values on the bars
    
    ax.set_title('Countplot of Categories')
    st.pyplot(fig)




@st.cache_data
def cached_scraper(youtube_api, video_url):
    return scraper(youtube_api, video_url)


def get_word_cloud(df, sentiment):
    sentiment = sentiment.lower()
    if sentiment in ('positive', 'negative', 'neutral'):
        data = df[df['sentiment'].str.lower().str.contains(sentiment)]['english_comm']
    else:
        data = df['english_comm']

    text = ' '.join(data.dropna().astype(str))

    wordcloud = WordCloud(width=1920, height=1080, background_color="white", max_words=50).generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

from collections import Counter

def get_bar_chart(df, sentiment):
    if sentiment.lower() in ('positive', 'negative', 'neutral'):
        data = df[df['sentiment'] == sentiment]['english_comm']
    else:
        data = df['english_comm']
    all_words = []
    data.apply(lambda x : all_words.extend(preprocess_text(x)))

    word_counts = Counter(all_words)
    most_common_words = word_counts.most_common(15)
    words, counts = zip(*most_common_words)

    fig, ax = plt.subplots(figsize = (10,6))
    ax.barh(words, counts, color = 'skyblue')
    ax.set_xlabel("Frequency",fontsize = 12)
    ax.set_ylabel("Words",fontsize = 12)
    ax.set_title("Top 15 most frequent keywords",fontsize = 14)
    plt.gca().invert_yaxis() # TO display the highest frequency at the top
    st.pyplot(fig)

def comments_trend_plot(df, sentiment):
    sentiment = sentiment.lower()

    # Filter data based on sentiment
    if sentiment in ('positive', 'negative', 'neutral'):
        data = df[df['sentiment'].str.lower().str.contains(sentiment)]['hour']
    else:
        data = df['hour']

    # Create the histogram
    fig, ax = plt.subplots(figsize=(10, 5))
    n, bins, patches = ax.hist(data, bins=24, range=(0, 25), edgecolor='black')  # Set range to 0-24 hours
    ax.set_title(f'Comments Trend by Hour ({sentiment.capitalize()})')
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Number of Comments')

    # Customize the x-axis ticks to display 0-24
    ax.set_xticks(range(0, 25))  # Set x-axis ticks from 0 to 24

    # Display the bar values (number of comments) on top of each bar
    for i in range(len(patches)):
        height = patches[i].get_height()
        ax.text(patches[i].get_x() + patches[i].get_width() / 2, height, 
                str(int(height)), ha='center', va='bottom', fontsize=10)

    # Display the plot in Streamlit
    st.pyplot(fig)


def toggle_data():
    st.session_state.show_data = not st.session_state.show_data


def toggle_plot():
    st.session_state.show_plot = not st.session_state.show_plot


    
youtube_api = st.secrets['YOUTUBE_API_KEY']
gemini_api = st.secrets['GEMINI_API_KEY']


### Main INterface### ---------------------------------------------------


st.header("Youtube Comments Sentiment Analyzer")
_,_,  col = st.columns([1,1,2])
col.subheader(" -by Siddhant Deokar")

# youtube, gemini, video = st.columns(3)

# youtube_api = youtube.text_input("Enter YouTube API Key", type='password', help="Your YouTube API key for fetching comments")    
# gemini_api = gemini.text_input("Enter Gemini API Key", type='password', help="Your Gemini API key for topic interpretation")trend
# video_url = video.text_input("Enter Video URL", help="URL of the YouTube video")

video_url = st.text_input("Enter Video URL", help="URL of the YouTube video")



df = None



if video_url:
    try:
        df = cached_scraper(youtube_api, video_url)
        
        ## Getting sentiment for 
        df['sentiment'] = df['english_comm'].apply(get_sentiment)
        st.session_state.df = df
        # st.balloons()
        st.success("Data fetched successfully!")
        video_info = get_video_info(video_url, youtube_api)
        channel = video_info['channel_name']
        title = video_info['video_title']
        st.subheader(f"Channel: {channel}")
        st.subheader(f"title: {title}")

    except:
        st.error("please enter a valid link")

else:
    st.error('Please fill in all the fields.')





# Display the plot or button based on the visibility state
if df is not None:
    
    st.header("Show Data")
   

    if st.session_state.show_data:
        st.write(df)
        st.button('Hide Data', on_click=toggle_data)
        
    else:
        # Show the button to show the countplot again
        st.button('Show Data', on_click=toggle_data)
        



    st.subheader("Summary of the Data")
    st.markdown(generate_summary(df))

    if st.session_state.show_plot:
        create_countplot()
        if st.button('Hide Countplot', key='hide_button', on_click=toggle_plot):
            pass  # toggle_plot function will be automatically called when button is clicked
    else:
        # Show the button to show the countplot again
        if st.button('Show Countplot', key='show_button', on_click=toggle_plot):
            pass  # toggle_plot function will be automatically called when button is clicked
            
    # show_trend
    st.subheader("Trend of Comment Posts Over Time by hour")
    trend_sentiment = st.selectbox("Enter Topic Sentiment (leave blank to choose whole data)",['','Positive','Neutral','Negative'], key = 'trend_sentiment')
    trend_plot = st.checkbox("Show Trend", key = 'trend_plot')
    if trend_plot:
            
        if trend_sentiment == '':
            st.subheader(f"Full Comments Trend")
        else:
            st.subheader(f"{trend_sentiment}")
        comments_trend_plot(df, trend_sentiment)
    # comments_trend_plot()

    st.header("Word Cloud")
    word_cloud_sentiment = st.selectbox("Enter Topic Sentiment (leave blank to choose whole data)",['','Positive','Neutral','Negative'],key = 'word_cloud_sentiment')
    show_cloud = st.checkbox("Show Word Cloud")
    
    if show_cloud:
        with st.spinner("Generating Word Cloud..."):
            
            if word_cloud_sentiment == '':
                st.subheader(f"Full Data Word Cloud")
            else:
                st.subheader(f"{word_cloud_sentiment}")
            get_word_cloud(df, word_cloud_sentiment)

    st.header("Frequent Words")
    
    freq_keyword_sentiment = st.selectbox("Enter Topic Sentiment (leave blank to choose whole data)",['','Positive','Neutral','Negative'],key = 'freq_keyword_sentiment')
    show_freq_keyword = st.checkbox("Show Frequent Keywords")
    if show_freq_keyword:
        with st.spinner("Finding Top 25 Keywords..."):
            
            if freq_keyword_sentiment == '':
                st.subheader(f"Most Frequent Keywords")
            else:
                st.subheader(f"{freq_keyword_sentiment} Sentiment Frequent Keywords")
            get_bar_chart(df, freq_keyword_sentiment)

    st.header("Topics")
    
    genai.configure(api_key=gemini_api)
    model = genai.GenerativeModel("gemini-1.5-flash")
    num = st.slider("Number of topics",2,5,3)

    topic_sentiment = st.selectbox("Enter Topic Sentiment (leave blank to choose whole data)",['','Positive','Neutral','Negative'], key ='topic_sentiment')

    get_topics_check = st.checkbox("Get Topics")
    if get_topics_check:
        if topic_sentiment and topic_sentiment.lower() not in ('','positive', 'neutral', 'negative'):
            st.error("Invalid sentiment. Please choose from 'positive', 'neutral', or 'negative'.")

        else:
            if topic_sentiment == '':
                st.subheader(f"Full Data Topics")
            else:
                st.subheader(f"{topic_sentiment}")
        
            x = get_topics(topic_sentiment, num,channel, title, model )
            st.markdown(print_topics(x), unsafe_allow_html=True)
            # st.write(x)




else:
    pass
