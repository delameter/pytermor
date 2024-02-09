//-----------------------------------------------------------------------------
// pytermor [ANSI formatted terminal output toolset]                          -
// (c) 2023. A. Shavykin <0.delameter@gmail.com>                              -
//-----------------------------------------------------------------------------

$(document).ready(function () {
    replaceControlCharacters();
    transformReferences();
    formatEnvLists();
    // formatEscCharLabels();  // now sphinx handles this
    squashNeighbourCodeSetions();
    removeBadgeBrackets();
    setExternalHrefTargetAndIcon();
    setXtermPaletteClickHandler();
});

function replaceControlCharacters() {
    for (let node of $("pre span.go, pre span.s1, p span.regex")) {
        node.textContent = node.textContent.replaceAll("", "\\x1b");
    }
}
function transformReferences() {
    for (let el of $(".field-list a.internal em, .field-list a strong, .field-list a.internal")) {
        if (el.firstChild.nodeType !== Node.TEXT_NODE) continue;
        let code = document.createElement('code');
        let span = document.createElement('span');
        code.classList.add('literal');
        span.classList.add('pre');
        span.innerHTML = el.innerHTML;
        code.appendChild(span);
        if (el.tagName.toLowerCase() === "em") {
            el.replaceWith(code);
        } else {
            el.firstChild.replaceWith(code);
        }
    }
    for (let el of $(".class .field-list dd:last-child > p:first-child")) {
        if (el.childNodes.length !== 1) continue;
        if (el.firstChild.nodeType !== Node.TEXT_NODE) continue;
        let em = document.createElement('em');
        em.textContent = el.textContent;
        el.replaceWith(em);
    }
}

function formatEnvLists() {
    $(".env-list dt").each((idx, el) => el.classList.add("sig"));
    $(".env-list .env").each((idx, el) => el.setAttribute("title", "Environment var"));
}

function squashNeighbourCodeSetions() {
    // find "highlight-adjacent"'s _preceeded_ by a div with a "highlight"
    // div inside and add adjacent classes to that parent div:
    //
    // <div> <!-- to this one -->
    //     <div="highlight"> ... </div>
    // </div>
    // <div "highlight-adjacent"> ... </div>
    //
    // $("div:has(div.highlight):has(+ div.highlight-adjacent)").each(
    //     (idx, el) => el.classList.add("highlight-adjacent")
    // );

    // actually found a bit better way; this will match all languages,
    // including .highlight-python and .highlight-console:
    $("div[class|=highlight]:has(+ div.highlight-adjacent)").each(
        (idx, el) => el.classList.add("highlight-adjacent")
    );
    // as of 2023 ":has" selector is not guaranteed to work in ALL browsers, but to hell with that
}

// function formatEscCharLabels() {
//     let affectedNodes = new Set();
//     for (let el of $('code:not(.xref) .pre')) {
//         if (!/^ESC$/.test(el.innerText)) continue;
//         el.classList.add("ansi");
//         // if we modify the DOM of the element while iterating its children, the
//         // child nodes after the current one will be missed out, as the cycle will
//         // continue to process nodes that are detached from DOM (don't know for sure
//         // though. at least that's what it looks like). one way to do it is to defer
//         // DOM updating. furthermore, storing the parent nodes in a set allows to
//         // avoid another DOM traversal and repeated processing of same parent nodes:
//         affectedNodes.add(el.parentNode);
//     }
//     affectedNodes.forEach(removeSpacesBetweenTags);
// }

function removeSpacesBetweenTags(el) {
    if (!el) return;
    el.innerHTML = el.innerHTML.replace(/>\s+</g, "><");
}

function setExternalHrefTargetAndIcon() {
    for (let el of $('a.external, a.internal.image-reference, .icons a')) {
        if (!el) continue;
        if (el.attributes.href.value.charAt(0) === '#') continue;

        let icon = document.createElement('i');
        icon.classList.add('fa', 'fa-external-link');
        el.appendChild(icon);
    }
}

let badgeContentMap = {
    "": "•",
    "[NEW]": "+",
    "[UPDATE]": "^",
    "[FIX]": "*",
    "[DOCS]": "#",
    "[TESTS]": "»",
    "[REFACTOR]": "±",
    "[CI/CD]": "@",
    "[REMOVE]": "×",
    "[REWORK]": "!",
}

function removeBadgeBrackets() {
    for (let el of $('span.badge')) {
        let t = el.textContent;
        const regex = /^$|^\[([A-Z/]*)]$/;
        if (regex.test(t)) {
            el.textContent = badgeContentMap[t];
            el.classList.remove("hidden");
            el.setAttribute('title', t.match(regex)[1] || '');
        }
    }
}

function setXtermPaletteClickHandler() {
    $(".xterm-palette tr div").click(function (e) {
            let el = e.currentTarget;
            el.data = el.ariaLabel;

            let text = [el.innerText, ...el.data.split(" · ")].join(" ");
            navigator.clipboard.writeText(text).then(function(){
                el.ariaLabel = "Copied to clipboard";
                setTimeout(() => el.ariaLabel = el.data, 500);
            });
        }
    );
}
