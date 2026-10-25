"""Edit In Place — правка полей прямо на карточке: при повторении и в окне «Просмотр».

Как Edit Field During Review: в шаблоне карточки поле пишется как {{edit:Поле}},
и его текст можно поправить щелчком (без Ctrl), не открывая редактор.
Главное отличие: поле с формулами тоже редактируется. Формулы MathJax
становятся нередактируемыми «островками» (отрисованы как обычно), правится
текст вокруг них, а при сохранении формулы возвращаются в поле в исходном
виде (подробности — logic.py и edit_in_place.js).

Формулы старого LaTeX Anki ([$]...[/$], [$$]...[/$$], [latex]...[/latex])
тоже становятся островками. Не редактируются (поле остаётся как есть):
пропуски {{c1::...}} и звук/видео [sound:...] — правка на карточке их бы испортила.

Сохранение — обычная операция Anki «Изменить запись»: её можно отменить
(Ctrl+Z / Правка → Отменить), карточка перерисовывается сама.
"""

from __future__ import annotations

import json

from anki import hooks as anki_hooks
from anki.template import TemplateRenderContext
from aqt import gui_hooks, mw
from aqt.browser.previewer import MultiCardPreviewer
from aqt.operations.note import update_note
from aqt.reviewer import Reviewer
from aqt.utils import tooltip
from aqt.webview import WebContent

from . import logic

ADDON = __name__.split(".")[0]
_JS_URL = f"/_addons/{ADDON}/edit_in_place.js"
_CSS = """
<style>
.eip-field { outline: none; border-radius: 4px; cursor: text; }
.eip-field:hover { box-shadow: 0 0 0 1px rgba(128, 128, 128, .35); }
.eip-field:focus { box-shadow: 0 0 0 2px rgba(80, 140, 255, .55); }
.eip-math { cursor: default; }
</style>
"""


def _config() -> dict:
    cfg = mw.addonManager.getConfig(ADDON) or {}
    return {"tag": "span" if cfg.get("tag") == "span" else "div"}


def on_field_filter(
    field_text: str, field_name: str, filter_name: str, ctx: TemplateRenderContext
) -> str:
    """Фильтр {{edit:Поле}}: делает поле редактируемым (если это безопасно)."""
    if filter_name != "edit":
        return field_text
    if not logic.can_edit(field_text):
        return field_text
    card = ctx.card()
    nid = card.nid if card is not None else ""
    return logic.wrap_field(field_text, field_name, nid, _config()["tag"])


def on_webview_will_set_content(web_content: WebContent, context: object) -> None:
    """Подключаем скрипт и стили на страницы повторения и предпросмотра."""
    if isinstance(context, (Reviewer, MultiCardPreviewer)):
        web_content.js.append(_JS_URL)
        web_content.head += _CSS


def _refresh(context: object) -> None:
    # Повторение перерисует карточку само (изменился текст записи);
    # предпросмотр пропускает перерисовку, если думает, что ничего не менялось.
    if isinstance(context, MultiCardPreviewer):
        context._last_state = None
        context.render_card()


def on_js_message(handled: tuple[bool, object], message: str, context: object):
    if not isinstance(message, str) or not message.startswith("eip-save:"):
        return handled
    if not isinstance(context, (Reviewer, MultiCardPreviewer)):
        return handled
    data = json.loads(message[len("eip-save:"):])
    try:
        note = mw.col.get_note(int(data["nid"]))
    except Exception:  # запись успели удалить
        return True, None
    field = data["field"]
    if field not in note.keys():
        return True, None
    new_html = logic.normalize_saved(data["html"])
    if note[field] == new_html:
        return True, None
    note[field] = new_html
    update_note(parent=mw, note=note).success(
        lambda _changes: _refresh(context)
    ).failure(lambda err: tooltip(f"Edit In Place: {err}")).run_in_background()
    return True, None


mw.addonManager.setWebExports(ADDON, r".*\.js")
anki_hooks.field_filter.append(on_field_filter)
gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
gui_hooks.webview_did_receive_js_message.append(on_js_message)
