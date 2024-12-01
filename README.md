# YouTube Comment Sentiment Analysis and Visualization

link:
```bash
https://youtube-comments-sentiment-analyzer.streamlit.app/
```

This Streamlit app allows you to scrape YouTube comments from a video, analyze their sentiment, visualize trends, and generate word clouds and topic extraction. 

### Features:
- **Scrape Comments**: Enter a YouTube video URL, fetch comments, and display the channel name and video title.
- **Comments DataFrame**: View or hide the comments dataframe, with an option to download it.
- **Sentiment Analysis**: See a summary of sentiment (positive, negative, neutral) for the comments.
- **Sentiment Distribution**: A count plot that shows the distribution of comment sentiments.
- **Comment Posting Trend**: Histogram showing the trend of comment posts over time by hour.
- **Word Cloud**: Visualize common words in the comments.
- **Frequent Words**: Bar plot showing the 15 most frequent words in the comments.
- **Topic Modeling**: Extract topics from the comments and visualize them.

<hr>

## Steps to Run the App Locally

### 1. Clone the repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/Siddhant-Deokar/youtube-comment-sentiment-analyzer
cd youtube-comment-sentiment-analyzer
```

### 2. Create a Virtual Environment

Next, create a Python virtual environment to isolate your project dependencies:

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

On Windows:
```bash
.\venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install the Dependencies

Install the required libraries using the requirements.txt file:

```bash
pip install -r requirements.txt
```

### 5. Run the Streamlit App

Start the Streamlit app with the following command:

```bash
streamlit run app.py
```

This will launch the app in your default web browser.

<hr>

## How to Use the App

### 1. Enter YouTube Video URL: 

In the text box, paste the URL of a YouTube video.

### 2. Fetch Comments: 
Click the button labeled "Fetch Comments". The app will scrape the comments from the video, display the video title and channel name, and show the comments in a dataframe.

### 3. View/Download Comments: 
You can toggle the visibility of the comments dataframe using the "Show/Hide Comments" button. If you'd like, you can download the comments as a CSV file.

### 4. Sentiment Analysis Summary: 
The app will display the sentiment analysis summary, showing the number of positive, neutral, and negative comments. It will also show the most common sentiment.

### 5. Sentiment Distribution Plot: 
A count plot of the sentiment distribution will be shown. You can toggle the plot visibility using the "Show/Hide Sentiment Distribution" button.

### 6. Trend of Comment Posts Over Time: 
View a histogram showing when comments were posted, grouped by hour. You can filter the plot by sentiment (positive, neutral, or negative) using the select box and toggle the plot visibility.

### 7. Word Cloud: 
The app generates a word cloud based on the comments. You can apply sentiment filters and toggle the visibility of the word cloud.

### 8. Frequent Words: 
A bar plot will display the 15 most frequent words across all comments.

### 9. Topic Modeling: 
Under the "Topics" section, you can specify the number of topics to extract from the comments. There is also an option to filter the topics by sentiment. If the checkbox is ticked, the app will display the extracted topics.

<hr>

## Dependencies
The project requires the following Python libraries:
* Streamlit
* NLTK
* Pandas
* Matplotlib
* Seaborn
* WordCloud
* Scikit-learn
* Plotly
* TextBlob
* Pytube
* Gensim
  
These are specified in the requirements.txt file.

