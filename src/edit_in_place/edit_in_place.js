// Edit In Place — правка полей {{edit:Поле}} прямо на карточке.
// Подключается один раз на страницу повторения и окна «Просмотр».
//
// Поле — элемент .eip-field[contenteditable]. Формулы внутри него — островки
// .eip-math (contenteditable=false) с исходником в data-eip-src (base64). При сохранении
// островки заменяются обратно на исходный текст формулы, так что в поле
// возвращается ровно то, что было, плюс правки текста вокруг.
(function () {
    "use strict";
    if (window.EIP_READY) return; // скрипт уже подключён
    window.EIP_READY = true;

    const FIELD = "[data-eip-field]";

    function fieldOf(node) {
        return node && node.closest ? node.closest(FIELD) : null;
    }

    // base64 → строка (UTF-8): исходник формулы из data-eip-src.
    function decodeSource(b64) {
        const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
        return new TextDecoder().decode(bytes);
    }

    // HTML поля с формулами-исходниками вместо отрисованных формул.
    function serialize(el) {
        const clone = el.cloneNode(true);
        const sources = [];
        clone.querySelectorAll(".eip-math").forEach((island, i) => {
            sources.push(decodeSource(island.getAttribute("data-eip-src")));
            island.replaceWith(document.createTextNode("\u0001EIP" + i + "\u0001"));
        });
        let html = clone.innerHTML;
        sources.forEach((src, i) => {
            html = html.split("\u0001EIP" + i + "\u0001").join(src);
        });
        return html;
    }

    // Запоминаем состояние при входе в поле — сохраняем, только если изменилось.
    document.addEventListener("focusin", (ev) => {
        const el = fieldOf(ev.target);
        if (el && el.eipOriginal === undefined) el.eipOriginal = serialize(el);
    });

    document.addEventListener("focusout", (ev) => {
        const el = fieldOf(ev.target);
        if (!el) return;
        const html = serialize(el);
        const original = el.eipOriginal;
        el.eipOriginal = undefined;
        if (html === original) return;
        pycmd(
            "eip-save:" +
                JSON.stringify({
                    field: el.getAttribute("data-eip-field"),
                    nid: el.getAttribute("data-eip-nid"),
                    html: html,
                })
        );
    });

    // Пока печатаешь в поле, клавиши не должны срабатывать как команды Anki
    // (пробел — показать ответ, цифры — оценка). Esc — закончить правку.
    document.addEventListener(
        "keydown",
        (ev) => {
            const el = fieldOf(ev.target);
            if (!el) return;
            if (ev.key === "Escape") {
                el.blur();
                ev.preventDefault();
            }
            ev.stopPropagation();
        },
        true
    );
})();
