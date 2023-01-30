//-----------------------------------------------------------------------------
// pytermor [ANSI formatted terminal output toolset]                          -
// (c) 2023. A. Shavykin <0.delameter@gmail.com>                              -
//-----------------------------------------------------------------------------

$(document).ready(function () {
    transformReferences();
    formatEnvLists();
    formatEscCharLabels();
    removeBadgeBrackets();
    setExternalHrefOpenMethodToBlank();
});

function transformReferences() {
    for (let el of $(".field-list a.internal em, .field-list a strong")) {
        el.outerHTML="<code class='literal'><span class='pre'>" + el.innerHTML + "</span></code>";
    }
    for (let el of $(".field-list a.external")) {
        if (el.childNodes.item(0).nodeType !== Node.TEXT_NODE)
            continue;
        if (/^\(in python/i.test(el.title))
            el.innerHTML="<code class='literal'><span class='pre'>" + el.innerHTML + "</span></code>";
    }
}

function formatEnvLists() {
    $(".env-list dt").each((idx, el) => el.classList.add("sig"));
}

function formatEscCharLabels() {
    let affectedNodes = new Set();
    for (let el of $('code:not(.xref) .pre')) {
        if (!/^ESC$/.test(el.innerText)) continue;
        el.classList.add("control-char");

        // if we modify the DOM of the element while iterating its children, the
        // child nodes after the current one will be missed out, as the cycle will
        // continue to process nodes that are detached from DOM (don't know for sure
        // though. at least that's what it looks like). one way to do it is to defer
        // DOM updating. furthermore, storing the parent nodes in a set allows to
        // avoid another DOM traversal and repeated processing of same parent nodes:
        affectedNodes.add(el.parentNode);
    }
    affectedNodes.forEach(removeSpacesBetweenTags);
}

function removeSpacesBetweenTags(el) {
    if (!el) return;
    el.innerHTML = el.innerHTML.replace(/>\s+</g, "><");
}

function setExternalHrefOpenMethodToBlank() {
    for (let el of $('a.external, a.internal.image-reference, .icons a')) {
        if (!el) continue;
        if (el.attributes.href.value.charAt(0) === '#') continue;
        el.setAttribute('target', '_blank');
    }
}

let badgeContentMap = {
    "": "•",
    "[NEW]": "+",
    "[FIX]": "*",
    "[DOCS]": "#",
    "[TESTS]": "»",
    "[REFACTOR]": "=",
}

function removeBadgeBrackets() {
    for (let el of $('span.badge')) {
        let t = el.textContent;
        const regex = /^$|^\[([A-Z]*)]$/;
        if (regex.test(t)) {
            el.textContent = badgeContentMap[t];
            el.classList.remove("hidden");
            el.setAttribute('title', t.match(regex)[1] || '');
        }
    }
}
