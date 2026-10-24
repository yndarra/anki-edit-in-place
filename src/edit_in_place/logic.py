"""Чистая логика без GUI (её проверяют тесты): что можно править и как защитить формулы.

Идея: поле {{edit:Поле}} становится редактируемым, а каждая формула MathJax
(\\(...\\) или \\[...\\]) оборачивается в «островок»:
    <span class="eip-math" contenteditable="false" data-tex="ИСХОДНИК">ИСХОДНИК</span>
MathJax отрисовывает формулу внутри островка как обычно, но править её щелчком
нельзя. Исходный текст формулы лежит в data-tex — при сохранении скрипт
страницы ставит его обратно вместо отрисованной формулы, поэтому формула
возвращается в поле буква в букву.
"""

from __future__ import annotations

import html
import re

# Формулы MathJax в Anki: \( ... \) — в строке, \[ ... \] — отдельным блоком.
MATH_RE = re.compile(r"\\\(.*?\\\)|\\\[.*?\\\]", re.DOTALL)

# То, что править на карточке нельзя совсем — иначе потеряются служебные теги:
CLOZE_RE = re.compile(r"\{\{c\d+::|<span class=\"?cloze", re.IGNORECASE)  # пропуски
SOUND_RE = re.compile(r"\[sound:", re.IGNORECASE)  # звук/видео (Anki заменяет на кнопку)
LATEX_RE = re.compile(r"\[latex\]|\[\$\$?\]", re.IGNORECASE)  # LaTeX-картинки


def can_edit(field_html: str) -> bool:
    """Можно ли сделать поле редактируемым на карточке."""
    return not (
        CLOZE_RE.search(field_html)
        or SOUND_RE.search(field_html)
        or LATEX_RE.search(field_html)
    )


def protect_formulas(field_html: str) -> str:
    """Каждую формулу — в нередактируемый островок с исходником в data-tex."""

    def wrap(match: re.Match[str]) -> str:
        source = match.group(0)
        return (
            '<span class="eip-math" contenteditable="false" '
            f'data-tex="{html.escape(source, quote=True)}">{source}</span>'
        )

    return MATH_RE.sub(wrap, field_html)


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
