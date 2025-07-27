import aiohttp

from src.config import TELEGRAPH_TOKEN
from typing import List, Dict, Union, Optional
from bs4 import BeautifulSoup, NavigableString, Tag

# --- правила из спецификации Telegraph ---
ALLOWED_TAGS: set[str] = {
    "a", "aside", "b", "blockquote", "br", "code", "em", "figcaption",
    "figure", "h3", "h4", "hr", "i", "iframe", "img", "li", "ol",
    "p", "pre", "s", "strong", "u", "ul", "video"
}
ALLOWED_ATTRS: dict[str, set[str]] = {
    "a": {"href"},
    "img": {"src"},
    "iframe": {"src"},
    "video": {"src"},
}

def _convert(node: Union[Tag, NavigableString]) -> Optional[Union[str, Dict, List]]:
    """
    Переводит один BeautifulSoup‑узел в формат Telegraph.
    Возвращает None, если узел бесполезен.
    """
    # --- текст ---
    if isinstance(node, NavigableString):
        txt = str(node)
        return txt if txt.strip() else None

    # --- не Tag (комментарий и т.п.) ---
    if not isinstance(node, Tag):
        return None

    # --- если тег запрещён — раскрываем детей ---
    if node.name not in ALLOWED_TAGS:
        children = [_convert(c) for c in node.children]
        # _convert может вернуть List, разворачиваем сразу
        flat = []
        for ch in children:
            if ch is None:
                continue
            flat.extend(ch) if isinstance(ch, list) else flat.append(ch)
        return flat or None

    # --- собираем NodeElement ---
    elem: Dict = {"tag": node.name}

    # разрешённые атрибуты
    for attr in ALLOWED_ATTRS.get(node.name, set()):
        if attr in node.attrs:
            elem.setdefault("attrs", {})[attr] = node[attr]

    # дети
    child_nodes = []
    for child in node.children:
        conv = _convert(child)
        if conv is None:
            continue
        child_nodes.extend(conv) if isinstance(conv, list) else child_nodes.append(conv)
    if child_nodes:
        elem["children"] = child_nodes

    return elem

def html_to_telegraph_content(html: str) -> List:
    """
    Принимает любой HTML‑фрагмент, возвращает Telegraph‑совместимый list.
    """
    soup = BeautifulSoup(html, "html.parser")
    roots = soup.body.contents if soup.body else soup.contents

    content: List = []
    for node in roots:
        conv = _convert(node)
        if conv is None:
            continue
        content.extend(conv) if isinstance(conv, list) else content.append(conv)
    return content


async def create_telegra_article(title: str, html_content: str):
    async with aiohttp.ClientSession() as session:
        content_nodes = html_to_telegraph_content(html_content)

        async with session.post("https://api.telegra.ph/createPage", json={
            "access_token": TELEGRAPH_TOKEN,
            "title": title,
            "content": content_nodes,
            "return_content": False
        }) as resp:
            data = await resp.json()
            return data["result"]["url"] if data["ok"] else None