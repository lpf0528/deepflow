import json

from langchain.tools import tool

def _search_images(query: str, size: str = None, color: str = None,
                   type_image: str = None, layout: str = None,
                   license_image: str = None, max_results: int = 5
                   ):
    from ddgs import DDGS

    ddgs = DDGS(timeout=30)
    results = ddgs.images(query, **{
        'region': 'wt-wt',  # No region,
        'safesearch': "moderate",  # Safe search level
        'size': size,  # Image size (Small/Medium/Large/Wallpaper)
        'color': color,  # Color filter
        'type_image': type_image,  # Image type (photo/clipart/gif/transparent/line)
        'layout': layout,  # Layout (Square/Tall/Wide)
        'license_image': license_image,  # License filter
    })
    return list(results) if results else []



@tool('image_search', parse_docstring=True)
def image_search_tool(query: str, max_results: int = 5, size: str = None,
                      type_image: str = None, layout: str = None) -> str:
    """在线搜索图片，再进行图像生成之前，使用此工具查找角色、肖像、物体、场景或任何需要视觉准确性的内容的参考图片。

    使用场景：
        * 在生成角色或肖像图像之前：搜索相似的姿势、表情、风格
        * 在生成特定物体或产品之前：搜索准确的视觉参考
        * 在生成场景或地点之前：搜索建筑或环境参考
        * 在生成时尚或服装内容之前：搜索风格和细节参考

    返回的图片 URL 可作为图像生成时的参考图像，从而显著提升生成质量

    Args:
        * query: 用于描述所需图片的搜索关键词。关键词越具体，效果越好（例如使用 “Japanese woman street photography 1990s” 而不是仅使用 “woman”）。
        * max_results: 返回图片的最大数量。默认值为 5。
        * size: 图片尺寸筛选。可选项包括 “Small”、“Medium”、“Large”、“Wallpaper”。如用于参考图片，建议选择 “Large”。
        * type_image: 图片类型筛选。可选项包括 “photo”、“clipart”、“gif”、“transparent”、“line”。如需真实感参考，建议选择 “photo”。
        * layout: 版式筛选。可选项包括 “Square”、“Tall”、“Wide”。根据生成需求进行选择。
    """

    results = _search_images(query, size=size, type_image=type_image, layout=layout, max_results=max_results)

    if not results:
        return json.dumps({"error": "未找到符合条件的图片", "query": query}, ensure_ascii=False)


    normalized_results = [{
        "title": result.get("title", ""),
        "image_url": result.get("thumbnail", ""),
        "thumbnail_url": result.get("thumbnail", "")
    } for result in results]

    return json.dumps({
        "query": query,
        'total_results': len(normalized_results),
        "results": normalized_results,
        'usage_hint': '使用"image_url"中的值作为图像生成的参考图像。必要时先下载这些图像。'
    }, ensure_ascii=False, indent=2)
