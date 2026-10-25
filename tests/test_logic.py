"""Тесты чистой логики (без Anki). Запуск: run_tests.bat."""

from __future__ import annotations

import base64
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "edit_in_place"))
import logic  # noqa: E402

FIELD = r"Что называется <b>длиной</b> вектора&nbsp;\(\vec{AB}\)? И ещё \[a<b\]"
# Оборот записи 1697282429733: старый LaTeX Anki [$]...[/$].
LEGACY = (
    "Векторы, имеющие противоположные направления, называют&nbsp;"
    "<b>противонаправленными</b><br><span class=\"c1\">"
    r"[$]\vec{a} \uparrow \downarrow \vec{b}[/$]</span>"
)


def restore_like_js(wrapped: str) -> str:
    """То же, что делает serialize() в edit_in_place.js: островок → его исходник."""

    def back(m: re.Match[str]) -> str:
        return base64.b64decode(m.group(1)).decode("utf-8")

    inner = re.sub(
        r'<span class="eip-math" contenteditable="false" data-eip-src="([^"]*)">.*?</span>',
        back, wrapped, flags=re.DOTALL,
    )
    return re.sub(r"^<div[^>]*>|</div>$", "", inner)


class LogicTest(unittest.TestCase):
    def test_mathjax_islands(self) -> None:
        out = logic.protect_formulas(FIELD)
        self.assertEqual(out.count('class="eip-math"'), 2)

    def test_legacy_latex_islands(self) -> None:
        out = logic.protect_formulas(LEGACY)
        self.assertEqual(out.count('class="eip-math"'), 1)
        # В атрибуте исходник закодирован — «[$]» встречается только в самом островке,
        # поэтому Anki заменит картинкой только содержимое, а не атрибут.
        self.assertEqual(out.count("[$]"), 1)
        for src in ("[$$]x[/$$]", "[latex]x^2[/latex]", "[LATEX]y[/latex]"):
            self.assertIn('class="eip-math"', logic.protect_formulas(src), src)

    def test_round_trip_keeps_field_exactly(self) -> None:
        for field in (FIELD, LEGACY, "текст без формул<br><br>ещё"):
            self.assertEqual(restore_like_js(logic.wrap_field(field, "Лицо", 1)), field)

    def test_can_edit(self) -> None:
        self.assertTrue(logic.can_edit(FIELD))
        self.assertTrue(logic.can_edit(LEGACY))
        self.assertTrue(logic.can_edit("<b>просто текст</b><br><br>ещё"))
        self.assertFalse(logic.can_edit("[sound:a.mp3]"))
        self.assertFalse(logic.can_edit("{{c1::Париж}}"))
        self.assertFalse(logic.can_edit('<span class="cloze">x</span>'))

    def test_wrap_field_attributes(self) -> None:
        out = logic.wrap_field("текст", 'По"ле', 42, "span")
        self.assertTrue(out.startswith('<span class="eip-field" contenteditable="true"'))
        self.assertIn('data-eip-field="По&quot;ле"', out)
        self.assertIn('data-eip-nid="42"', out)

    def test_normalize(self) -> None:
        self.assertEqual(logic.normalize_saved("<br>"), "")
        self.assertEqual(logic.normalize_saved("a<br>"), "a<br>")


if __name__ == "__main__":
    unittest.main()
