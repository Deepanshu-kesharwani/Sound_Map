import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="SoundMap",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with improved styling
st.markdown("""
<style>
    /* Main theme colors and styles */
    :root {
        --background-color: #1e1e1e;
        --card-background: #2d2d2d;
        --text-color: #ffffff;
        --accent-color: #1DB954;
        --error-color: #ff4444;
    }

    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* Song card styling */
    .song-card {
        padding: 1.5rem;
        background-color: var(--card-background);
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out;
    }

    .song-card:hover {
        transform: translateY(-2px);
    }

    /* YouTube container styling */
    .youtube-container {
        position: relative;
        padding-bottom: 56.25%;
        height: 0;
        overflow: hidden;
        max-width: 100%;
        border-radius: 8px;
        margin-top: 1rem;
    }

    .youtube-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 8px;
    }

    /* Custom button styling */
    .stButton button {
        background-color: var(--accent-color);
        color: white;
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
        border: none;
        transition: all 0.2s ease-in-out;
    }

    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Constants
BACKEND_URL = "http://localhost:8000"
CACHE_DURATION = 300  # 5 minutes in seconds


class MusicApp:
    def __init__(self):
        # Initialize session state
        if 'current_song' not in st.session_state:
            st.session_state.current_song = None
        if 'last_search_time' not in st.session_state:
            st.session_state.last_search_time = {}
        if 'search_cache' not in st.session_state:
            st.session_state.search_cache = {}

    @staticmethod
    def display_song_card(track: Dict[str, Any], button_key: str) -> None:
        """Display a song card with play button"""
        col_info, col_button = st.columns([3, 1])

        with col_info:
            st.markdown(f"""
            <div class="song-card">
                <h3>{track['name']}</h3>
                <p>Artist: {track['artist']}</p>
                <p>Last played: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_button:
            if st.button("▶ Play", key=button_key):
                st.session_state.current_song = track
                st.experimental_rerun()

    def display_now_playing(self) -> None:
        """Display the currently playing song"""
        st.subheader("🎵 Now Playing")
        if st.session_state.current_song:
            song = st.session_state.current_song
            st.markdown(f"""
            <div class="song-card">
                <h3>{song['name']}</h3>
                <p>Artist: {song['artist']}</p>
                <div class="youtube-container">
                    <iframe
                        src="https://www.youtube.com/embed/{song['youtube_id']}?autoplay=1"
                        frameborder="0"
                        allow="autoplay; encrypted-media"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def fetch_recommendations(self) -> None:
        """Fetch and display song recommendations"""
        try:
            with st.spinner("Loading recommendations..."):
                response = requests.get(f"{BACKEND_URL}/recommendations")
                response.raise_for_status()
                recommendations = response.json()

                for rec in recommendations:
                    if rec.get('youtube_id'):
                        self.display_song_card(rec, f"play_rec_{rec['name']}_{rec['artist']}")

        except requests.RequestException as e:
            logger.error(f"Error fetching recommendations: {str(e)}")
            st.error("Unable to fetch recommendations. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            st.error("An unexpected error occurred. Please try again later.")

    def search_songs(self, query: str) -> None:
        """Search for songs and display results"""
        # Check cache first
        cache_key = query.lower()
        current_time = time.time()

        if (cache_key in st.session_state.search_cache and
                current_time - st.session_state.last_search_time.get(cache_key, 0) < CACHE_DURATION):
            results = st.session_state.search_cache[cache_key]
        else:
            try:
                with st.spinner("Searching..."):
                    response = requests.get(
                        f"{BACKEND_URL}/search",
                        params={"query": query}
                    )
                    response.raise_for_status()
                    results = response.json()

                    # Update cache
                    st.session_state.search_cache[cache_key] = results
                    st.session_state.last_search_time[cache_key] = current_time

            except requests.RequestException as e:
                logger.error(f"Search error: {str(e)}")
                st.error("Unable to perform search. Please try again later.")
                return
            except Exception as e:
                logger.error(f"Unexpected error during search: {str(e)}")
                st.error("An unexpected error occurred. Please try again later.")
                return

        # Display results
        if results:
            st.subheader(f"🔍 Search Results for '{query}'")
            for track in results:
                if track.get('youtube_id'):
                    self.display_song_card(track, f"play_{track['name']}_{track['artist']}")
        else:
            st.info("No results found. Try a different search term.")

    def run(self):
        """Main application logic"""
        st.title("🎵 SoundMap")

        # Create main layout
        col1, col2 = st.columns([2, 1])

        with col2:
            self.display_now_playing()

        with col1:
            # Search section
            search_query = st.text_input("🔍 Search for songs...",
                                         placeholder="Enter song or artist name")
            if search_query:
                self.search_songs(search_query)

            # Recommendations section
            st.subheader("📈 Recommended for You")
            self.fetch_recommendations()


if __name__ == "__main__":
    app = MusicApp()
    app.run()