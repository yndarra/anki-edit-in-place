"""Чистая логика без GUI (её проверяют тесты): что можно править и как защитить формулы.

Идея: поле {{edit:Поле}} становится редактируемым, а каждая формула
оборачивается в «островок»:
    <span class="eip-math" contenteditable="false" data-eip-src="BASE64">ИСХОДНИК</span>
Формула внутри островка отрисовывается как обычно, но править её щелчком
нельзя. Исходный текст формулы лежит в data-eip-src — при сохранении скрипт
страницы ставит его обратно вместо отрисованной формулы, поэтому формула
возвращается в поле буква в букву.

Формулы бывают двух видов:
  • MathJax: \\(...\\) — в строке, \\[...\\] — отдельным блоком;
  • старый LaTeX Anki: [$]...[/$], [$$]...[/$$], [latex]...[/latex] — Anki
    превращает их в картинку при отрисовке.
Исходник хранится в base64: Anki ищет [$]...[/$] по всему HTML карточки,
в том числе внутри атрибутов, и в открытом виде подменила бы его картинкой
прямо в атрибуте — разметка сломалась бы.
"""

from __future__ import annotations

import base64
import html
import re

# Все виды формул. [$$] проверяется раньше [$], иначе «[$$]» разобрался бы как «[$]».
FORMULA_RE = re.compile(
    r"\\\(.*?\\\)"            # MathJax в строке
    r"|\\\[.*?\\\]"           # MathJax блоком
    r"|\[latex\].*?\[/latex\]"
    r"|\[\$\$\].*?\[/\$\$\]"
    r"|\[\$\].*?\[/\$\]",
    re.DOTALL | re.IGNORECASE,
)

# То, что править на карточке нельзя совсем — иначе потеряются служебные теги:
CLOZE_RE = re.compile(r"\{\{c\d+::|<span class=\"?cloze", re.IGNORECASE)  # пропуски
SOUND_RE = re.compile(r"\[sound:", re.IGNORECASE)  # звук/видео (Anki заменяет на кнопку)


def can_edit(field_html: str) -> bool:
    """Можно ли сделать поле редактируемым на карточке."""
    return not (CLOZE_RE.search(field_html) or SOUND_RE.search(field_html))


def encode_source(source: str) -> str:
    return base64.b64encode(source.encode("utf-8")).decode("ascii")


def protect_formulas(field_html: str) -> str:
    """Каждую формулу — в нередактируемый островок с исходником в data-eip-src."""

    def wrap(match: re.Match[str]) -> str:
        source = match.group(0)
        return (
            '<span class="eip-math" contenteditable="false" '
            f'data-eip-src="{encode_source(source)}">{source}</span>'
        )

    return FORMULA_RE.sub(wrap, field_html)


def wrap_field(field_html: str, field_name: str, nid: int | str, tag: str = "div") -> str:
    """Готовая разметка редактируемого поля для шаблона карточки."""
    return (
        f'<{tag} class="eip-field" contenteditable="true" '
        f'data-eip-field="{html.escape(field_name, quote=True)}" data-eip-nid="{nid}">'
        f"{protect_formulas(field_html)}</{tag}>"
    )


def normalize_saved(field_html: str) -> str:
    """Пустое поле браузер отдаёт как <br> — сохраняем как пустую строку."""
    return "" if field_html.strip() in ("<br>", "<div><br></div>") else field_html
