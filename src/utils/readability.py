from markdownify import markdownify as md
from readabilipy import simple_json_from_html_string

class Article:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content

    def to_markdown(self) -> str:
        markdown = f'# {self.content}\n\n'
        if not self.content:
            markdown += "*No content available.*\n"
        else:
            markdown += md(self.content)

        return markdown


class ReadabilityExtractor:
    def extract_article(self, html_content: str) -> Article:
        article = simple_json_from_html_string(html_content, use_readability=True)
        title = article.get('title', '')
        if not title or not title.strip():
            title = "Untitled"
        content = article.get('content', '')
        if not content or not content.strip():
            content = "Failed to extract content from the URL"
        return Article(title, content)
