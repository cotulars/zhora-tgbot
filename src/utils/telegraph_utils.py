import aiohttp

from src.config import TELEGRAPH_TOKEN


async def create_telegra_article(title: str, html_content: str):
    async with aiohttp.ClientSession() as session:
        # Надо преобразовать HTML в JSON content
        def convert_html_to_nodes(html_conten: str):
            return [{"tag": "p", "children": [html_conten]}]

        content_nodes = convert_html_to_nodes(html_content)

        async with session.post("https://api.telegra.ph/createPage", json={
            "access_token": TELEGRAPH_TOKEN,
            "title": title,
            "content": content_nodes,
            "return_content": False
        }) as resp:
            data = await resp.json()
            return data["result"]["url"] if data["ok"] else None