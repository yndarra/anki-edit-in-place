# Edit In Place (formula-safe)

An Anki add-on for editing card fields right on the card, both during review and in the browser's **Preview** window, without opening the editor. Mark a field in the card template as `{{edit:Field}}` and click its text to edit it. No Ctrl is needed.

The difference from [Edit Field During Review](https://ankiweb.net/shared/info/1020366288) is that **fields with MathJax formulas stay editable**. Each formula (MathJax `\(...\)` / `\[...\]` and old Anki LaTeX `[$]...[/$]`, `[$$]...[/$$]`, `[latex]...[/latex]`) becomes a protected "island": it is rendered as usual, but you can't change it by clicking. You edit the text around it, and on save every formula goes back into the field exactly as it was written. The original add-on refuses to edit any field that contains even one formula.

- Save: click outside the field or press **Esc**. This is a normal "Update Note" operation, so **Ctrl+Z** undoes it.
- While you type in a field, keys don't trigger Anki shortcuts (Space, rating keys).
- Not editable, to protect them: cloze fields `{{c1::…}}` and sound/video `[sound:…]`.
- Without the add-on (mobile, another computer), `{{edit:Field}}` is ignored and the field shows normally.

Install from AnkiWeb: code **1244274740** ([ankiweb.net/shared/info/1244274740](https://ankiweb.net/shared/info/1244274740)).

Development: `run_tests.bat`, `build.bat`. Requires Anki 23.10+. Tested with 26.09: formulas, preview and review were checked in a real Anki instance.

---

# Правка на карточке с формулами (RU)

Поле `{{edit:Поле}}` правится щелчком при повторении и в окне «Просмотр», без Ctrl. Формулы становятся нередактируемыми «островками»: правится текст вокруг них, а сами формулы при сохранении возвращаются в поле в исходном виде. Сохранение — щелчок мимо или Esc, отмена — Ctrl+Z.

## License
MIT
