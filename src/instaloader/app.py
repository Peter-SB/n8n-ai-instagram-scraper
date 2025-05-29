import re
import sys
import logging
from flask import Flask, request, jsonify
from instaloader import Instaloader, Post

logger = logging.getLogger(__name__)
app = Flask(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
    force=True
)

L = Instaloader(
        dirname_pattern="/data/instaloader/{shortcode}", 
        filename_pattern="{shortcode}", 
        download_comments=False)

def scrape_post(shortcode):
    post = Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target=shortcode)

    logger.info(f"Downloaded post for: {shortcode}")

    return jsonify({
        "shortcode": shortcode,
        "video": f"/data/instaloader/{shortcode}/{shortcode}.mp4",
        "description": post.caption or ""
    })

def extract_shortcode(url):
    match = re.search(r'(?:reel|p)/([A-Za-z0-9_-]+)/', url)
    if not match:
        logger.info(f"Error: Could not extract shortcode from URL '{url}'")
        return jsonify({"error": "Invalid URL format"}), 400
    
    return match.group(1)

@app.route("/scrape", methods=["POST"])
def scrape():
    logger.info("Starting Instaloader Job")
    
    # Extract the URL from the request
    data = request.get_json()
    url = data.get("url")
    if not url:
        logger.warning("Missing 'url' in request.")
        return jsonify({"error": "Missing 'url'"}), 400

    # Extract the shortcode from the URL
    shortcode = extract_shortcode(url)
    
    # Scrape the post
    logger.info(f"Scraping Instagram post with shortcode: {shortcode}")
    try:
        return scrape_post(shortcode)
    except Exception as e:
        logger.error(f"Error scraping post {shortcode}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    logger.debug("Health check called.")
    return "OK", 200

if __name__ == "__main__":
    logger.info("Starting Instaloader Flask app...")
    app.run(host="0.0.0.0", port=5633)
