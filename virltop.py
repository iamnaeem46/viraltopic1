import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyCelOVWXb6wIietQ1Yo1nNmIC791qtYrk4"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# List of broader keywords
keywords = [
    "Chosen Ones", "Spiritual Awakening", "Chosen Ones Spiritual", "Spiritual", 
    "Cheat Exposed"
]

# Fetch Data Button
if st.button("Fetch Viral Videos"):
    try:
        # Calculate date range (Last 30 days)
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat("T") + "Z"
        all_results = []

        # Iterate over the list of keywords
        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")
            
            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 10,
                "videoDuration": "medium",  # Exclude YouTube Shorts
                "relevanceLanguage": "en",  # Fetch only English videos
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos]

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data:
                st.warning(f"Failed to fetch video statistics for keyword: {keyword}")
                continue

            # Collect results with 50K+ views
            for video, stat in zip(videos, stats_data["items"]):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                channel_id = video["snippet"]["channelId"]
                views = int(stat["statistics"].get("viewCount", 0))
                
                if views >= 50000:
                    # Fetch channel details
                    channel_params = {"part": "statistics", "id": channel_id, "key": API_KEY}
                    channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
                    channel_data = channel_response.json()

                    if "items" in channel_data and channel_data["items"]:
                        subscribers = int(channel_data["items"][0]["statistics"].get("subscriberCount", 0))
                        
                        if subscribers >= 1000:
                            all_results.append({
                                "Title": title,
                                "Description": description,
                                "URL": video_url,
                                "Views": views,
                                "Subscribers": subscribers
                            })

        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} viral videos!")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}  "
                )
                st.write("---")
        else:
            st.warning("No viral videos found with more than 50,000 views in the last 30 days.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
