import streamlit as st
import preprocessor
import helper
import plotly.express as px
import plotly.graph_objects as go


import io
import zipfile

# st.sidebar.title('WhatsApp Chat Analyser')
# Page config
st.set_page_config(page_title="WhatsApp Analyzer", page_icon="💬", layout="wide")

# Custom CSS for better styling


st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #FFFFFF;
    }
    div[data-testid="stMetricLabel"] {
        color: #A0A0A0;
    }
    .big-font {
        font-size: 3rem !important;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    h2, h3 {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)
# Sidebar styling
st.sidebar.markdown("""
    <h1 style='text-align: center; color: #667eea;'>💬 WhatsApp Chat Analyzer</h1>
    """, unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader(
    "📁 Choose a WhatsApp chat file",
    type=['txt', 'zip']
)

if uploaded_file is not None:

    data = None  # this will store chat text

    # ---------- CASE 1: TXT FILE ----------
    if uploaded_file.name.endswith('.txt'):
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode('utf-8')

    # ---------- CASE 2: ZIP FILE ----------
    elif uploaded_file.name.endswith('.zip'):
        with zipfile.ZipFile(uploaded_file) as z:
            # find the chat txt file
            txt_files = [f for f in z.namelist() if f.endswith('.txt')]

            if not txt_files:
                st.error("❌ No chat .txt file found inside ZIP")
                st.stop()

            # usually only one chat file exists
            with z.open(txt_files[0]) as f:
                data = f.read().decode('utf-8')

    df = preprocessor.preprocess(data)




    # Extract no.of unique users


    # Extract only the user part before the first colon
    df['users'] = (
        df['users']
        .str.strip()
        .str.replace(r'\s+' , ' ', regex = True )
    )
    # Remove 'group_notification' (case-insensitive)
    df = df[df['users'] != 'group_notification']
    user_list = (
        df['users'].unique().tolist()
    )

    user_list.sort()
    user_list.insert(0, 'Overall')


    selected_user = st.sidebar.selectbox("👤 Show analysis for", user_list)

    if st.sidebar.button("🚀 Show Analysis", use_container_width=True):

        # Header
        st.markdown("<p class='big-font'>📊 Chat Analytics Dashboard</p>", unsafe_allow_html=True)
        st.markdown("---")

        # Stats Area with animated metrics
        num_messages, words, num_media_messages, num_links = helper.fetch_statistics(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💬 Total Messages", f"{num_messages:,}", delta="Messages")
        with col2:
            st.metric("📝 Total Words", f"{words:,}", delta="Words")
        with col3:
            st.metric("🎬 Media Shared", f"{num_media_messages:,}", delta="Files")
        with col4:
            st.metric("🔗 Links Shared", f"{num_links:,}", delta="URLs")

        st.markdown("---")

        # Sentiment Analysis Section
        st.markdown("<h2 style='text-align: center; color: #667eea;'>😊 Emotional Tone of Messages</h2>", unsafe_allow_html=True)

        sentiment_stats = helper.sentiment_analysis(selected_user, df)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("😊 Positive", f"{sentiment_stats['positive']:.1f}%",
                      delta=f"{sentiment_stats['positive']:.1f}%", delta_color="normal")
        with col2:
            st.metric("😐 Neutral", f"{sentiment_stats['neutral']:.1f}%",
                      delta=f"{sentiment_stats['neutral']:.1f}%", delta_color="off")
        with col3:
            st.metric("❌ Negative", f"{sentiment_stats['negative']:.1f}%",
                      delta=f"-{sentiment_stats['negative']:.1f}%", delta_color="inverse")

        # Animated Sentiment Pie Chart
        fig = go.Figure(data=[go.Pie(
            labels=['Positive 😊', 'Neutral 😐', 'Negative 😞'],
            values=[sentiment_stats['positive'], sentiment_stats['neutral'], sentiment_stats['negative']],
            hole=.4,
            marker=dict(colors=['#10b981', '#fbbf24', '#ef4444'],
                        line=dict(color='#FFFFFF', width=3)),
            textfont=dict(size=16, color='white'),
            hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'
        )])

        fig.update_layout(
            title={
                'text': '🎭 Sentiment Distribution',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#667eea'}
            },
            showlegend=True,
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Sentiment Timeline
        st.markdown("<h2 style='text-align: center; color: #667eea;'>📈 Chat Mood Over Time</h2>",
                    unsafe_allow_html=True)

        sentiment_timeline = helper.sentiment_timeline(selected_user, df)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=sentiment_timeline['date'], y=sentiment_timeline['positive'],
            name='Positive', mode='lines+markers',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8, symbol='circle'),
            fill='tonexty', fillcolor='rgba(16, 185, 129, 0.2)'
        ))

        fig.add_trace(go.Scatter(
            x=sentiment_timeline['date'], y=sentiment_timeline['neutral'],
            name='Neutral', mode='lines+markers',
            line=dict(color='#fbbf24', width=3),
            marker=dict(size=8, symbol='square'),
            fill='tonexty', fillcolor='rgba(251, 191, 36, 0.2)'
        ))

        fig.add_trace(go.Scatter(
            x=sentiment_timeline['date'], y=sentiment_timeline['negative'],
            name='Negative', mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=8, symbol='diamond'),
            fill='tonexty', fillcolor='rgba(239, 68, 68, 0.2)'
        ))

        fig.update_layout(
            title='Sentiment Trends',
            xaxis_title='Date',
            yaxis_title='Percentage (%)',
            hovermode='x unified',
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            font=dict(size=14)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")



        # WordCloud
        st.markdown("<h2 style='text-align: center; color: #667eea;'>☁️ Common Chat Words</h2>", unsafe_allow_html=True)
        df_wc = helper.create_wordcloud(selected_user, df)

        fig = go.Figure()
        fig.add_layout_image(
            dict(source=df_wc.to_image(),
                 xref="paper", yref="paper",
                 x=0, y=1,
                 sizex=1, sizey=1,
                 sizing="contain",
                 layer="below")
        )

        fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
        fig.update_layout(height=600,
                          margin=dict(l=0, r=0, t=0, b=0),
                          xaxis=dict(visible=False),
                          yaxis=dict(visible=False)

                          )

        st.plotly_chart(fig, use_container_width=True)




        # Monthly Timeline
        st.markdown("<h2 style='text-align: center; color: #667eea;'>📅 Monthly Activity</h2>", unsafe_allow_html=True)
        timeline = helper.monthly_timeline(selected_user, df)

        fig = px.line(timeline, x='time', y='message',
                      title='Messages Over Months',
                      labels={'time': 'Month-Year', 'message': 'Number of Messages'})

        fig.update_traces(line_color='#667eea', line_width=3,
                          mode='lines+markers', marker=dict(size=10))
        fig.update_layout(height=500, hovermode='x',
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(255,255,255,0.9)')

        st.plotly_chart(fig, use_container_width=True)



        st.markdown("---")

        # Activity Map
        st.markdown("<h2 style='text-align: center; color: #667eea;'>⚡ Activity Patterns</h2>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Peak Chat Day")
            busy_day = helper.week_activity_map(selected_user, df)

            fig = px.bar(x=busy_day.index, y=busy_day.values,
                         labels={'x': 'Day', 'y': 'Messages'},
                         color=busy_day.values,
                         color_continuous_scale='Purples')

            fig.update_layout(showlegend=False, height=400,
                              paper_bgcolor='rgba(17, 24, 39, 1)' ,
                              plot_bgcolor='rgba(255,255,255,0.9)')

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 Most Active Chat Month")
            busy_month = helper.month_activity_map(selected_user, df)

            fig = px.bar(x=busy_month.index, y=busy_month.values,
                         labels={'x': 'Month', 'y': 'Messages'},
                         color=busy_month.values,
                         color_continuous_scale='Oranges')

            fig.update_layout(showlegend=False, height=400,
                              paper_bgcolor='rgba(15, 23, 42, 0.95)',
                              plot_bgcolor='rgba(255,255,255,0.9)')

            st.plotly_chart(fig, use_container_width=True)

        # Heatmap
        # st.markdown("<h2 style='text-align: center; color: #667eea;'>🔥 Weekly Activity Heatmap</h2>",
        #             unsafe_allow_html=True)
        # user_heatmap = helper.activity_heatmap(selected_user, df)
        #
        # fig = go.Figure(data=go.Heatmap(
        #     z=user_heatmap.values,
        #     x=user_heatmap.columns,
        #     y=user_heatmap.index,
        #     colorscale='Viridis',
        #     hovertemplate='Day: %{y}<br>Time: %{x}<br>Messages: %{z}<extra></extra>'
        # ))
        #
        # fig.update_layout(
        #     title='Activity Heatmap (Day vs Time)',
        #     xaxis_title='Time Period',
        #     yaxis_title='Day of Week',
        #     height=500,
        #     paper_bgcolor='rgba(0,0,0,0)',
        #     plot_bgcolor='rgba(255,255,255,0.9)'
        # )
        #
        # st.plotly_chart(fig, use_container_width=True)
        #
        # st.markdown("---")

        # Most Busy Users (Group level)
        if selected_user == 'Overall':
            st.markdown("<h2 style='text-align: center; color: #667eea;'>👥 Most Active Users</h2>",
                        unsafe_allow_html=True)
            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)
            # Example


            # Your gradient colors from left to right (peach → dark purple)

            with col1:
                fig = px.bar(
                    x=x.index,
                    y=x.values,
                    labels={'x': 'User', 'y': 'Messages'},
                    title='Top 5 Active Users',
                    color=x.values,
                    color_continuous_scale=[
                        'rgb(255, 204, 204)',  # light peach
                         'rgb(255, 153, 204)',  # pink
                         'rgb(204, 102, 204)',  # medium purple
                          'rgb(153, 51, 153)',  # dark purple
                           'rgb(77, 0, 77)'  # darkest purple # still darkish red, avoid pale
                    ]
                )

                fig.update_layout(
                    showlegend=False,
                    height=500,
                    font_color='black',  # avoid white text
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    xaxis=dict(tickfont=dict(color='rgba(200, 200, 200, 0.95)')),
                    yaxis=dict(tickfont=dict(color='rgba(200, 200, 200, 0.95)'))
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("📋 User Statistics")
                st.dataframe(new_df, use_container_width=True, height=500)

        st.markdown("---")


        # Most Common Words
        st.markdown("<h2 style='text-align: center; color: #667eea;'>🔤 Most Common Words</h2>", unsafe_allow_html=True)
        most_common_df = helper.most_common_words(selected_user, df)

        fig = px.bar(most_common_df, x=1, y=0, orientation='h',
                     labels={'1': 'Frequency', '0': 'Words'},
                     title='Top 20 Most Used Words',
                     color=1,
                     color_continuous_scale='Blues')

        fig.update_layout(showlegend=False, height=600,
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(173,216,230,0.9)',

                          yaxis={'categoryorder': 'total ascending'})

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Emoji Analysis
        st.markdown("<h2 style='text-align: center; color: #667eea;'>😀 Emoji Analysis</h2>", unsafe_allow_html=True)
        emoji_df = helper.emoji_helper(selected_user, df)

        if not emoji_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Top Emojis")
                st.dataframe(emoji_df.head(10), use_container_width=True, height=400)

            with col2:
                fig = px.pie(emoji_df.head(10), values=1, names=0,
                             title='Top 10 Emoji Distribution',
                             hole=0.4)

                fig.update_traces(textposition='inside', textinfo='percent+label',
                                  marker=dict(line=dict(color='#FFFFFF', width=2)))

                fig.update_layout(height=400,
                                  paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(255,255,255,0.9)',
                                  showlegend=False)

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No emojis found in the selected chat!")

        # Footer
        st.markdown("---")


    else:
        # Welcome screen
        st.markdown("""
                <div style='text-align: center; padding: 50px;'>
                    <h1 style='color: #667eea; font-size: 4rem;'>💬 WhatsApp Chat Analyzer</h1>
                    <p style='font-size: 1.5rem; color: #764ba2;'>Upload your WhatsApp chat export to get started!</p>
                    <p style='font-size: 1.2rem; margin-top: 30px;'>📱 Export your chat from WhatsApp → More options → Export chat</p>
                </div>
            """, unsafe_allow_html=True)





