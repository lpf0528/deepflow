import json
import os
from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv



@tool('web_search', parse_docstring=True)
def web_search_tool(query: str) -> str:
    """互联网上搜索内容。

    Args:
        query:  要搜索的查询。
    """

    max_results = 5
    client = TavilyClient(api_key=os.environ['TAVILY_API_KEY'])
    res = client.search(query, max_results=max_results)
    # 标准化结果
    normalized_results = [
        {
            "title": item["title"],
            "url": item["url"],
            "snippet": item["content"]  # 取的简短内容片段
        }
        for item in res["results"]
    ]

    json_result = json.dumps(normalized_results, ensure_ascii=False, indent=2)
    return json_result
