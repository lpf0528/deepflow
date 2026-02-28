from langchain.tools import tool
import requests
import os
from src.utils.readability import ReadabilityExtractor



class JinaClient:

    def crawl(self, url: str, return_format: str = 'html', timeout: int = 30) -> str:
        try:
            response = requests.post('https://r.jina.ai/', headers={
                "Content-Type": "application/json",
                "X-Return-Format": return_format,
                "X-Timeout": str(timeout),
                "Authorization": f"Bearer {os.environ['JINA_API_KEY']}"
            }, json={"url": url})
            if response.status_code != 200:
                error_message = f"Jina API returned non-200 status code: {response.status_code}"
                return f"Error: {error_message}"
            if not response.text or not response.text.strip():
                error_message = "Jina API returned empty response"
                return f"Error: {error_message}"
        except requests.RequestException as e:
            error_message = f"Request to Jina API failed: {str(e)}"
            return f"Error: {error_message}"
        return response.text



@tool('web_fetch', parse_docstring=True)
def web_fetch_tool(url: str) -> str:
    """ 获取指定 URL 的网页内容。
    仅允许抓取用户直接提供的精确 URL，或通过 web_search 与 web_fetch 工具返回结果中的 URL。
    该工具无法访问需要身份验证的内容，例如私有的 Google Docs 或需要登录才能访问的页面。
    不要为原本不包含 www的 URL 添加 www.
    URL 必须包含协议（schema），例如 https://example.com是有效 URL，而 example.com 是无效 URL。

    Args:
        url:  需要获取内容的网页地址。
    """
    jina_client = JinaClient()
    html_content = jina_client.crawl(url, return_format="html", timeout=30)
    # readabilipy:用于从网页中提取主要内容，比如文章的标题、正文和元数据
    extractor = ReadabilityExtractor()
    article = extractor.extract_article(html_content)
    return article.to_markdown()[:4096]
