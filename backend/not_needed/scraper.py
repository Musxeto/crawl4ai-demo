import asyncio
import re
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from sqlalchemy import Column, Integer, String
from database import Base, engine, SessionLocal

# Define the Video model
class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    url = Column(String(255), unique=True, nullable=False)
    channel = Column(String(255), default="Unknown")
    views = Column(String(50))
    uploaded = Column(String(100))
    thumbnail = Column(String(1000))  # Increased from VARCHAR(255) to VARCHAR(1000)

# Create tables in MySQL
Base.metadata.create_all(bind=engine)

async def scrape_youtube():
    """Scrapes YouTube search results using crawl4ai."""
    browser_config = BrowserConfig(verbose=True)
    run_config = CrawlerRunConfig(
        word_count_threshold=10,
        excluded_tags=['form', 'header'],
        exclude_external_links=True,
        process_iframes=True,
        remove_overlay_elements=True,
        cache_mode=CacheMode.ENABLED
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://www.youtube.com/results?search_query=crawl4ai+full+tutorial",
            config=run_config
        )

        if result.success:
            return extract_data(result.markdown)
        else:
            print(f"Crawl failed: {result.error_message}")
            return None

def extract_data(markdown):
    """Extracts structured video data from the crawled markdown text."""
    extracted_videos = []
    video_blocks = markdown.split("\n\n")  # Splitting by empty lines to get separate video entries

    for block in video_blocks:
        lines = block.split("\n")
        current_video = {}

        for line in lines:
            # Extract URL
            if "](https://www.youtube.com/watch?" in line:
                match = re.search(r"\((https://www.youtube.com/watch\?v=[^)]*)\)", line)
                if match:
                    current_video["url"] = match.group(1)

            # Extract Title
            title_match = re.search(r"\[([^\]]+)\]\(", line)
            if title_match:
                current_video["title"] = title_match.group(1).strip()

            # Extract Channel Name
            if "views" not in line and "ago" not in line and "https://i.ytimg.com/" not in line:
                if "channel" not in current_video:
                    current_video["channel"] = line.strip()

            # Extract Views and Upload Time
            if "views" in line and "ago" in line:
                parts = line.split(" ")
                current_video["views"] = parts[0] + " " + parts[1]
                current_video["uploaded"] = " ".join(parts[2:])

            # Extract Thumbnail
            if "https://i.ytimg.com/" in line:
                match = re.search(r"(https://i.ytimg.com/[^)]+)", line)
                if match:
                    current_video["thumbnail"] = match.group(1).split(")")[0]  # Clean thumbnail URL

        if current_video:
            extracted_videos.append(current_video)

    return extracted_videos

def save_to_database(videos):
    """Saves extracted video data to the database."""
    session = SessionLocal()
    
    for video in videos:
        print(f"Title: {video['title']}, URL: {video['url']}, Channel: {video['channel']}, "
              f"Views: {video['views']}, Uploaded: {video['uploaded']}, Thumbnail: {video['thumbnail']}")

        existing_video = session.query(Video).filter_by(url=video.get("url")).first()
        if existing_video:
            print(f"Skipping duplicate: {video.get('title')}")
            continue

        new_video = Video(
            title=video.get("title", "Unknown Title"),
            url=video.get("url"),
            channel=video.get("channel", "Unknown"),
            views=video.get("views", "0 views"),
            uploaded=video.get("uploaded", "Unknown upload date"),
            thumbnail=video.get("thumbnail", "")
        )

        session.add(new_video)

    session.commit()
    session.close()

async def main():
    """Main function to scrape YouTube and save data to the database."""
    videos = await scrape_youtube()
    if videos:
        save_to_database(videos)
        print(f"Stored {len(videos)} videos in the database.")

if __name__ == "__main__":
    asyncio.run(main())
