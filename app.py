from flask import Flask, jsonify, request
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_videos():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    results = []
    with sync_playwright() as p:
        # Chupa hua Chrome browser kholein
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # User ki tarah DuckDuckGo videos par search karein
            search_url = f"https://duckduckgo.com{query}&iax=videos&ia=videos"
            page.goto(search_url, timeout=30000)

            # Videos load hone ka intezar karein
            page.wait_for_selector(".tile--vid", timeout=10000)

            # Screen se pehli 15 videos ka data uthayein
            videos = page.query_selector_all(".tile--vid")
            for vid in videos[:15]:
                title_el = vid.query_selector(".tile__title a")
                img_el = vid.query_selector(".tile__media__img")

                if title_el and img_el:
                    title = title_el.inner_text().strip()
                    video_link = title_el.get_attribute("href")
                    photo = img_el.get_attribute("src")

                    # Agar photo link mein https nahi hai to lagayein
                    if photo and photo.startswith("//"):
                        photo = "https:" + photo

                    results.append({
                        "title": title,
                        "photo": photo,
                        "video_link": video_link
                    })
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
