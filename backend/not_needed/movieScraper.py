import re
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

from database import SessionLocal
from models import Movie

def parse_movies_from_markdown(markdown_text):
    """
    Extract movie details from the markdown content.
    """
    movies = []
    movie_pattern = re.compile(
        r"\*\*(.*?)\*\*.*?Showtime: (.*?)\n.*?Price: (\d+\.\d+).*?Location: (.*?)\n.*?Seats Available: (\d+)", re.DOTALL
    )

    for match in movie_pattern.finditer(markdown_text):
        movies.append({
            "title": match.group(1),
            "show_time": match.group(2),
            "price": float(match.group(3)),
            "location": match.group(4),
            "seats_available": int(match.group(5))
        })

    return movies

def insert_movie_data(movies):
    """
    Insert a list of movie data into the database.
    """
    session = SessionLocal()
    try:
        for movie in movies:
            new_movie = Movie(
                title=movie["title"],
                show_time=movie["show_time"],
                price=movie["price"],
                location=movie["location"],
                seats_available=movie["seats_available"]
            )
            session.add(new_movie)
        
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error inserting data:", e)
    finally:
        session.close()
        
async def main():
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
        results = await crawler.arun(
            url="https://www.amazon.com/Best-Sellers-Books/zgbs/books",
            config=run_config
        )

        if isinstance(results, list):  # Check if multiple results are returned
            for result in results:
                if result.success:
                    print(f"Crawling completed for {result.url}")
                    print(result.markdown)

                    movies = parse_movies_from_markdown(result.markdown)
                    if movies:
                        insert_movie_data(movies)
                        print("Movies inserted successfully!")
                    else:
                        print(f"No movie data found for {result.url}")
                else:
                    print(f"Crawl failed for {result.url}: {result.error_message}")
        else:  # If only one result is returned
            if results.success:
                print("Crawling completed successfully.")
                print(results.markdown)
                movies = parse_movies_from_markdown(results.markdown)

                if movies:
                    insert_movie_data(movies)
                    print("Movies inserted successfully!")
                else:
                    print("No movie data found.")

            else:
                print(f"Crawl failed: {results.error_message}")

if __name__ == "__main__":
    asyncio.run(main())

