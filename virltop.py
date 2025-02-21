import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key (Replace with your own key)
API_KEY = "AIzaSyDq85dFBHd70pQS_01PL98J5LnOuOl-Lhc"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# Streamlit App Title
st.title("YouTube Viral Video Finder")

# List of Keywords
keywords = [
    "Chosen Ones", "Spiritual Awakening", "Manifestation", "Law of Attraction",
    "Spiritual Journey", "Higher Consciousness", "Mindfulness", "Subconscious Mind",
    "Meditation", "Divine Energy", "Spirituality", "Self-Realization", "Inner Peace"
]

# Fetch Data Button
if st.button("Find Viral Videos"):
    try:
        # Calculate date range (Last 30 days)
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat("T") + "Z"
        all_results = []

        # Iterate over the keywords
        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")
            
            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 20,
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
                views = int(stat["statistics"].get("viewCount", 0))

                if views >= 50000:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views
                    })
                
                # Stop when we reach 10 videos
                if len(all_results) >= 10:
                    break

            if len(all_results) >= 10:
                break

        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} viral videos!")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  "
                )
                st.write("---")
        else:
            st.warning("No viral videos found with more than 50,000 views in the last 30 days.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
