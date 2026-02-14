#!/usr/bin/env python3
"""
URL to EPUB Converter
輸入網址，將網頁轉換成 EPUB 電子書
"""

import sys
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import re
import os

def fetch_page(url):
    """取得網頁內容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def parse_html(html, url):
    """解析 HTML，提取標題和內容"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 取得標題
    title = soup.find('title')
    title = title.get_text(strip=True) if title else "Untitled"
    
    # 移除 script 和 style 標籤
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    
    # 取得主要內容
    main_content = soup.find('main') or soup.find('article') or soup.find('body')
    
    # 清理標題中的非法字元
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    
    return title, main_content.get_text(separator='\n', strip=True) if main_content else ""

def create_epub(title, content, url, output_path):
    """建立 EPUB 檔案"""
    book = epub.EpubBook()
    
    # 設定書籍資訊
    book.set_identifier(f'url2epub_{hash(url)}')
    book.set_title(title)
    book.set_language('zh-TW')
    book.add_author('URL to EPUB Converter')
    
    # 建立章節
    chapter = epub.EpubHtml(title=title, file_name='chapter1.xhtml', lang='zh-TW')
    chapter.content = f'''
    <html>
    <head><title>{title}</title></head>
    <body>
        <h1>{title}</h1>
        <p>來源：<a href="{url}">{url}</a></p>
        <hr/>
        <pre>{content}</pre>
    </body>
    </html>
    '''
    book.add_item(chapter)
    
    # 建立目錄
    book.toc = (epub.Link('chapter1.xhtml', title, 'chapter1'),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # 加入 CSS
    style = '''
    body { font-family: Times New Roman, serif; line-height: 1.6; }
    h1 { text-align: center; }
    pre { white-space: pre-wrap; word-wrap: break-word; }
    '''
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    book.spine = ['nav', chapter]
    
    # 儲存檔案
    epub.write_epub(output_path, book, {})
    return output_path

def main():
    if len(sys.argv) < 2:
        print("用法: python url2epub.py <網址> [輸出檔名]")
        print("範例: python url2epub.py https://example.com mybook.epub")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"正在處理: {url}")
    
    # 取得網頁
    print("正在抓取網頁...")
    html = fetch_page(url)
    
    # 解析內容
    print("正在解析內容...")
    title, content = parse_html(html, url)
    
    # 產生輸出檔名
    if not output_file:
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)[:50]
        output_file = f"{safe_title}.epub"
    
    # 建立 EPUB
    print(f"正在建立 EPUB: {output_file}")
    create_epub(title, content, url, output_file)
    
    print(f"✅ 完成！檔案已儲存: {output_file}")
    print(f"   標題: {title}")
    print(f"   字數: {len(content)}")

if __name__ == "__main__":
    main()
