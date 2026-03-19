from playwright.sync_api import sync_playwright
import os
import time

base_url = "https://www.example.com"
blog_listing_url = f"{base_url}/blogs"
output_dir = "/path/to/store/output"
os.makedirs(output_dir, exist_ok=True)

blog_links = []

with sync_playwright() as p:
    print("🚀 Launching browser...")
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        locale="it-IT",
        viewport={"width": 1280, "height": 800}
    )
    page = context.new_page()

    # Step 1: Open blog listing page
    print(f"🌐 Opening: {blog_listing_url}")
    page.goto(blog_listing_url, wait_until="networkidle")
    time.sleep(3)

    # Step 2: Keep clicking "Carica altro" until all 69 posts loaded
    print("\n🔍 Loading all blog posts...\n")
    while True:
        # Count visible blog posts
        links = page.eval_on_selector_all(
            "a[href*='/case-study/'], a[href*='/knowledge-centre/podcast/'], a[href*='/knowledge-centre/webinar/']",
            "elements => elements.map(el => el.href)"
        )
        print(f"📄 Blog posts visible so far: {len(links)}")

        # Check if "Carica altro" (Load More) button exists
        load_more = page.query_selector("a[rel='next']")

        if load_more:
            print("⏭️  Clicking 'Carica altro'...")
            load_more.scroll_into_view_if_needed()
            load_more.click()
            time.sleep(3)
            page.wait_for_load_state("networkidle")
        else:
            print("✅ All posts loaded!")
            blog_links = list(set(links))
            break

    print(f"\n📊 Total unique blog posts found: {len(blog_links)}")

    # Save URLs to text file
    urls_file = "/Users/path/projects/dep/all-blog-urls.txt"
    with open(urls_file, "w") as f:
        for link in blog_links:
            f.write(link + "\n")
    print(f"✅ URLs saved to {urls_file}\n")

    # Step 3: Visit and save each blog post
    print("📥 Downloading all blog posts...\n")
    for i, link in enumerate(blog_links, 1):
        print(f"[{i}/{len(blog_links)}] Downloading: {link}")
        try:
            page.goto(link, wait_until="networkidle")
            time.sleep(2)

            html_content = page.content()
            filename = link.rstrip("/").split("/")[-1] + ".html"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"  💾 Saved: {filename}")

        except Exception as e:
            print(f"  ❌ Failed: {link} → {e}")

    browser.close()

print(f"\n🎉 Done! {len(blog_links)} blog posts saved to {output_dir}")
