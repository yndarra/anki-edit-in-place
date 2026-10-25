<b>Edit card fields right on the card, during review and in the Browser's Preview window. No Ctrl needed, and fields with formulas stay editable.</b>

Mark a field in the card template as <code>{{edit:Field}}</code> (for example <code>{{edit:Back}}</code>), then click its text on the card and type.

<ul>
<li><b>Formula-safe:</b> MathJax <code>\(...\)</code> / <code>\[...\]</code> and old Anki LaTeX <code>[$]...[/$]</code>, <code>[$$]...[/$$]</code>, <code>[latex]...[/latex]</code> become protected "islands". They render as usual and can't be changed by a click. You edit the text around them, and on save every formula goes back into the field exactly as it was written. (Edit Field During Review refuses to edit a field that contains even one formula.)</li>
<li>Works in review <b>and</b> in the Browser's Preview window.</li>
<li>No modifier key: just click the text.</li>
<li>To save, click outside the field or press <b>Esc</b>. It is a normal "Update Note" operation, so <b>Ctrl+Z</b> undoes it.</li>
<li>While you type, keys don't trigger Anki shortcuts (Space, rating keys).</li>
<li>Cloze fields <code>{{c1::…}}</code> and sound/video <code>[sound:…]</code> are left read-only to protect them.</li>
<li>Without the add-on (mobile, another computer), <code>{{edit:Field}}</code> is ignored and the field shows normally.</li>
</ul>

Conflicts with Edit Field During Review (1020366288) and its Cloze variant (385888438). Disable those before you use this one.

Tested with Anki 26.09. Requires 23.10+.

Source code and tests: <a href="https://github.com/yndarra/anki-edit-in-place">github.com/yndarra/anki-edit-in-place</a>

<i>RU: правка полей прямо на карточке при повторении и в «Просмотре», без Ctrl; формулы остаются нетронутыми.</i>
