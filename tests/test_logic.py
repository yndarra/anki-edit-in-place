"""Тесты чистой логики (без Anki). Запуск: run_tests.bat."""

from __future__ import annotations

import html
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "edit_in_place"))
import logic  # noqa: E402

FIELD = r"Что называется <b>длиной</b> вектора&nbsp;\(\vec{AB}\)? И ещё \[a<b\]"


def restore_like_js(wrapped: str) -> str:
    """То же, что делает serialize() в edit_in_place.js: островок → его data-tex."""

    def back(m: re.Match[str]) -> str:
        return html.unescape(m.group(1))

    inner = re.sub(r'<span class="eip-math" contenteditable="false" data-tex="([^"]*)">.*?</span>',
                   back, wrapped, flags=re.DOTALL)
    return re.sub(r"^<div[^>]*>|</div>$", "", inner)


class LogicTest(unittest.TestCase):
    def test_formulas_become_islands(self) -> None:
        out = logic.protect_formulas(FIELD)
        self.assertEqual(out.count('class="eip-math"'), 2)
        self.assertIn(r'data-tex="\(\vec{AB}\)"', out)
        # «<» внутри формулы экранирован в атрибуте и не ломает разметку.
        self.assertIn(r'data-tex="\[a&lt;b\]"', out)

    def test_round_trip_keeps_field_exactly(self) -> None:
        wrapped = logic.wrap_field(FIELD, "Лицо", 123)
        self.assertEqual(restore_like_js(wrapped), FIELD)

    def test_can_edit(self) -> None:
        self.assertTrue(logic.can_edit(FIELD))
        self.assertTrue(logic.can_edit("<b>просто текст</b><br><br>ещё"))
        self.assertFalse(logic.can_edit("[sound:a.mp3]"))
        self.assertFalse(logic.can_edit("{{c1::Париж}}"))
        self.assertFalse(logic.can_edit('<span class="cloze">x</span>'))
        self.assertFalse(logic.can_edit("[latex]x^2[/latex]"))

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
