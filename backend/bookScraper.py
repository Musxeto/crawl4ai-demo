import re
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

from database import SessionLocal
from models import Book  

def parse_books_from_markdown(markdown_text):
    """
    Extract book details from the markdown content using regex.
    """
    book_pattern = re.findall(
        r'#(\d+)\s*\n'  # Extracts ranking
        r'\[\!\[(.*?)\]\((.*?)\)\]\((https:\/\/www\.amazon\.com\/.*?)\)\n'
        r'([^\n]+)\n'
        r'([^$]+)\n',
        markdown_text
    )

    books = []
    for ranking, title, image_url, product_url, author, price in book_pattern:
        books.append({
            "ranking": int(ranking),  # Convert to integer
            "title": title.strip(),
            "author": author.strip(),
            "image_url": image_url.strip(),
            "product_url": product_url.strip()
        })

    return books
def insert_book_data(books):
    """
    Insert a list of book data into the database.
    """
    session = SessionLocal()
    try:
        print("Inserting book data...")
        for book in books:
            new_book = Book(
                ranking=book["ranking"],
                title=book["title"],
                author=book["author"],
                image_url=book["image_url"],
                product_url=book["product_url"]
            )
            session.add(new_book)
        
        session.commit()
        print("Books inserted successfully!")
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
            url="https://www.amazon.com/Sunrise-Reaping-Hunger-Games-Novel/dp/1546171460/ref=zg_bs_g_books_d_sccl_2/140-5066547-9894520?psc=1",
            config=run_config
        )

        if isinstance(results, list):  
            for result in results:
                if result.success:
                    print(f"Crawling completed for {result.url}")
                    print(result.text)
                    print(result.markdown)

                    books = parse_books_from_markdown(result.markdown)
                    if books:
                        insert_book_data(books)
                    else:
                        print(f"No book data found for {result.url}")
                else:
                    print(f"Crawl failed for {result.url}: {result.error_message}")
        else:  
            if results.success:
                print("Crawling completed successfully.")
                print(results.markdown)
                books = parse_books_from_markdown(results.markdown)

                if books:
                    insert_book_data(books)
                else:
                    print("No book data found.")
            else:
                print(f"Crawl failed: {results.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
