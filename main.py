import streamlit as st
import os
import yt_dlp
import requests

def test_url(url):
    """Test if the URL is reachable"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        return f"URL check failed: {str(e)}"

def download_video(url, resolution, download_type, output_path):
    try:
        # Test URL first
        url_status = test_url(url)
        if url_status is not True:
            st.error(f"URL validation failed: {url_status}")
            return

        # Create placeholder for progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Configure yt-dlp options
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': f'bestvideo[height<={resolution[:-1]}]+bestaudio/best' if download_type == "Video" else 'bestaudio',
            'merge_output_format': 'mp4' if download_type == "Video" else 'mp3',
            'quiet': False,
            'no_warnings': False,
        }

        # Progress callback function
        def progress_hook(d):
            if d['status'] == 'downloading':
                # Extract percentage from string and convert to float
                percent_str = d.get('_percent_str', '0%').strip().replace('%', '')
                try:
                    percent = float(percent_str) / 100
                    progress_bar.progress(min(percent, 1.0))  # Ensure it doesn't exceed 100%
                    status_text.text(f"Downloading: {percent_str}% complete")
                except ValueError:
                    status_text.text("Downloading: Processing...")
            elif d['status'] == 'finished':
                progress_bar.progress(1.0)
                status_text.text("Download finished, processing...")

        ydl_opts['progress_hooks'] = [progress_hook]

        # Attempt download
        st.write(f"Attempting to download from: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if download_type == "Audio":
                filename = os.path.splitext(filename)[0] + '.mp3'

            st.success(f"Download completed! File saved to: {filename}")

            # Offer file download
            with open(filename, "rb") as file:
                st.download_button(
                    label="Download File",
                    data=file,
                    file_name=os.path.basename(filename),
                    mime="video/mp4" if download_type == "Video" else "audio/mp3"
                )

    except yt_dlp.utils.DownloadError as e:
        st.error(f"Download error: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")

def main():
    st.title("YouTube Downloader (Enhanced)")
    st.write("Enter a YouTube URL and select your download preferences")

    # Input fields
    url = st.text_input("YouTube URL", "")
    download_type = st.selectbox("Download Type", ["Video", "Audio"])
    
    resolution = None
    if download_type == "Video":
        resolution = st.selectbox(
            "Resolution",
            ["1080p", "720p", "480p", "360p", "240p", "144p"]
        )

    output_path = st.text_input("Output Directory", value=os.getcwd())

    # Download button
    if st.button("Download"):
        if not url:
            st.error("Please enter a YouTube URL")
        elif not url.startswith(('http://', 'https://')):
            st.error("Please enter a valid URL starting with http:// or https://")
        elif not os.path.isdir(output_path):
            st.error("Please enter a valid output directory")
        else:
            with st.spinner("Initializing download..."):
                download_video(url, resolution, download_type, output_path)

    # Troubleshooting info
    with st.expander("Troubleshooting"):
        st.write("""
        If you encounter issues:
        1. Verify the URL is correct and public
        2. Check your internet connection
        3. Try a different YouTube video
        4. Ensure yt-dlp is updated: `pip install --upgrade yt-dlp`
        5. The video might be region-restricted or age-restricted
        """)

if __name__ == "__main__":
    main()