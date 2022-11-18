/*---------------------------------------------------------------------------*/
/* pytermor [ANSI formatted terminal output toolset]                         */
/* (c) 2022. A. Shavykin <0.delameter@gmail.com>                             */
/*---------------------------------------------------------------------------*/

$(document).ready(function () {
    $('a.external, a.internal.image-reference').attr('target', '_blank');
    $('code:not(.xref) .pre').each(customizeElement);
});

function customizeElement(idx, el) {
    if (/^ESC$/.test(el.innerText)){
        el.classList.add("control-char");
        removeSpacesBetweenTags(el.parentNode);
    }
}
function removeSpacesBetweenTags(el) {
    if (el.innerHTML.search(/>\s+</) !== -1) {
        console.debug(el.innerHTML)
    }
    el.innerHTML = el.innerHTML.replace(/>\s+</g, "><");
}
