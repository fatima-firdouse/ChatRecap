
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
from textblob import TextBlob




def fetch_statistics(selected_user, df):

    if selected_user != 'Overall':
        df= df[df['users'] == selected_user]

    # total_msgs
    total_msgs = df.shape[0]

    # total words
    words = []
    for m in df['message']:
        words.extend(m.split())

    total_words = len(words)


    # total media
    # total_media = df[df['messages'] == "<Media omitted>\n"].shape[0]
    total_media = df['message'].str.contains('Media omitted', na=False).sum()
    # total links
    extract = URLExtract()
    links = []
    for m in df['message']:
        links.extend(extract.find_urls(m))
    total_links = len(links)

    return total_msgs, total_words,total_media, total_links


def sentiment_analysis(selected_user, df):
    """Analyze sentiment of messages"""
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    # Filter out group notifications and media messages

    temp = df[df['message'] != '<Media omitted>\n']

    sentiments = []
    for message in temp['message']:
        try:
            # Analyze sentiment using TextBlob
            analysis = TextBlob(message)
            polarity = analysis.sentiment.polarity

            # Classify sentiment
            if polarity > 0.1:
                sentiments.append('positive')
            elif polarity < -0.1:
                sentiments.append('negative')
            else:
                sentiments.append('neutral')
        except:
            sentiments.append('neutral')

    # Calculate percentages
    sentiment_counts = Counter(sentiments)
    total = len(sentiments)

    if total == 0:
        return {'positive': 0, 'neutral': 0, 'negative': 0}

    return {
        'positive': (sentiment_counts['positive'] / total) * 100,
        'neutral': (sentiment_counts['neutral'] / total) * 100,
        'negative': (sentiment_counts['negative'] / total) * 100
    }

def sentiment_timeline(selected_user, df):
    """Get sentiment trends over time"""
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    # Filter out group notifications and media messages

    temp = df[df['message'] != '<Media omitted>\n'].copy()

    # Add sentiment column
    sentiments = []
    for message in temp['message']:
        try:
            analysis = TextBlob(message)
            sentiments.append(analysis.sentiment.polarity)
        except:
            sentiments.append(0)

    temp['sentiment'] = sentiments

    # Group by date and calculate average sentiment
    daily_sentiment = temp.groupby('only_date').agg({
        'sentiment': lambda x: sum(1 for s in x if s > 0.1) / len(x) * 100 if len(x) > 0 else 0
    }).reset_index()
    daily_sentiment.columns = ['date', 'positive']

    # Calculate neutral and negative
    temp_grouped = temp.groupby('only_date')

    neutral_pct = []
    negative_pct = []

    for date in daily_sentiment['date']:
        date_messages = temp[temp['only_date'] == date]['sentiment']
        total = len(date_messages)
        if total > 0:
            neutral = sum(1 for s in date_messages if -0.1 <= s <= 0.1) / total * 100
            negative = sum(1 for s in date_messages if s < -0.1) / total * 100
        else:
            neutral = 0
            negative = 0
        neutral_pct.append(neutral)
        negative_pct.append(negative)

    daily_sentiment['neutral'] = neutral_pct
    daily_sentiment['negative'] = negative_pct

    return daily_sentiment


# def most_busy_users(df):
#     x = df['users'].value_counts().head()
#     df_percent = round((df['users'].value_counts() / df.shape[0]) * 100, 2).reset_index()
#     df_percent.columns = ['name', 'percent']
#     return x, df_percent


def most_busy_users(df):

    user_counts = df['users'].value_counts()

    top_users = user_counts.head()

    percent_df = (
        (user_counts / user_counts.sum()) *100
    ).round(2).reset_index()

    percent_df.columns = ['User', 'Percentage (%)']

    return  top_users, percent_df


def create_wordcloud(selected_user , df):

    try:
        with open('stop_hinglish.txt' , 'r') as f:
            stop_words = set(f.read().split())

    except FileNotFoundError:
        stop_words = set()


    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    temp = df[df['message'] != '<Media omitted>\n'].copy()

    def remove_stop_words(message):
        y = []
        for w in message.lower().split():
            if w not in stop_words:
                y.append(w)
        return ' '.join(y)

    wc = WordCloud(width = 1600 ,
                   height=800 ,
                   min_font_size=30 ,
                   max_font_size=350,
                   max_words=200,
                   background_color='white',
                   scale = 3,
                   collocations=False)

    temp = temp.copy()
    temp['message'] = temp['message'].apply(remove_stop_words)
    text = temp['message'].str.cat(sep = ' ')

    return  wc.generate(text)



def most_common_words(selected_user, df):
    try:
        f = open('stop_hinglish.txt', 'r')
        stop_words = f.read()
        f.close()
    except FileNotFoundError:
        stop_words = ""

    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]


    temp = df[df['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    if len(emojis) == 0:
        return pd.DataFrame()

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    timeline = df.groupby(['year', 'month_no', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    daily_timeline1 = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline1


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap