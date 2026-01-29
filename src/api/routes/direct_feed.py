"""Direct feed endpoint using GraphQL method"""
from fastapi import APIRouter
from typing import List, Dict
import asyncio
import json
from playwright.async_api import async_playwright
from pathlib import Path

router = APIRouter()

@router.get("/feed/direct")
async def get_direct_feed(limit: int = 10) -> List[Dict]:
    """Get feed directly using GraphQL interception - bypasses cache"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1024})
        
        cookies_file = Path(__file__).parent.parent.parent.parent / 'cookies' / 'default.json'
        with open(cookies_file) as f:
            await context.add_cookies(json.load(f)['cookies'])
        
        page = await context.new_page()
        
        post_urls = set()
        
        async def handle_response(response):
            if '/api/graphql/' in response.url and response.status == 200:
                try:
                    text = await response.text()
                    for line in text.split('\n'):
                        if line.strip():
                            data = json.loads(line)
                            extract_urls(data, post_urls)
                except:
                    pass
        
        page.on('response', handle_response)
        
        await page.goto("https://www.facebook.com/mark.retallack", wait_until='networkidle')
        await asyncio.sleep(3)
        
        for _ in range(3):
            await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
        
        page.remove_listener('response', handle_response)
        
        posts = []
        for url in list(post_urls)[:limit]:
            try:
                await page.goto(url, wait_until='networkidle', timeout=10000)
                await asyncio.sleep(1)
                
                if '/photo/' in url:
                    text = await page.get_attribute('meta[name="description"]', 'content', timeout=5000) or ""
                else:
                    article = await page.query_selector('[role="article"]')
                    if article:
                        text_elems = await article.query_selector_all('[dir="auto"]')
                        texts = [await e.inner_text() for e in text_elems[:3]]
                        text = '\n'.join([t.strip() for t in texts if t.strip()])
                    else:
                        text = ""
                
                if text:
                    posts.append({
                        'id': url,
                        'author': {'name': 'Mark Retallack', 'profile_url': 'https://www.facebook.com/mark.retallack'},
                        'content': text,
                        'url': url
                    })
            except:
                pass
        
        await browser.close()
        return posts

def extract_urls(data, urls):
    if isinstance(data, dict):
        for key, value in data.items():
            if key in ['permalink_url', 'wwwURL', 'url'] and isinstance(value, str):
                if '/posts/' in value or '/photo/' in value:
                    urls.add(value)
            elif isinstance(value, (dict, list)):
                extract_urls(value, urls)
    elif isinstance(data, list):
        for item in data:
            extract_urls(item, urls)
