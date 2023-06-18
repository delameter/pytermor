#!/bin/bash
#------------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]                           -
# (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>                          -
# Licensed under GNU Lesser General Public License v3.0                       -
#------------------------------------------------------------------------------

PROJECT_NAME="${1:?Project name required}"
DEPENDS_PATH="${2:?Output path required}"

LOW_LEVEL_GROUP_COLOR=5f819d
INTERM_LEVEL_GROUP_COLOR=5e8d87
HIGH_LEVEL_GROUP_COLOR=769440

run() {
    # args: [cmd-option]...
    export PT_ENV=build
    export PT_QUIET=true
    set -- ./.invoke pydeps "${PROJECT_NAME}" "$@"
    echo "$*" >&2
    "$@"
}

postprocess_module() {
    local tpl_path="${DOCS_IN_PATH}/_generated/module.dot.tpl"
    declare -i placheolder_lineno=$(grep -nm1 -Ee '^\s*%s\s*$' < "$tpl_path" | cut -f1 -d:)
    {
        head -n $((placheolder_lineno-1)) "$tpl_path"
        sed -Ee '/^\s*pytermor/!d;'\
             -e '/_ansi|_conv|_config|_color|_parser|_term/ s/(fillcolor="#)[0-9a-f]+(")/group="low",\1'$LOW_LEVEL_GROUP_COLOR'\2/;'\
             -e '/_cval/ s/(fillcolor="#)[0-9a-f]+(")/group="high",\1'$INTERM_LEVEL_GROUP_COLOR'\2/;'\
             -e '/_style|_filter|_renderer|_text|_numfmt|_template/ s/(fillcolor="#)[0-9a-f]+(")/group="high",\1'$HIGH_LEVEL_GROUP_COLOR'\2/;'\
             -e '/->/ s/group="[a-z]+",//g; '
        tail -n +$((placheolder_lineno+1)) "$tpl_path"
    } | tee "${DOCS_IN_PATH}/_generated/module.dot"
}

run --rmprefix "${PROJECT_NAME}". \
    --only "${PROJECT_NAME}" \
    --no-output \
    --rankdir TB \
    --show-dot \
    -xx pytermor \
        pytermor._version \
        pytermor.common \
        pytermor.exception \
        pytermor.log \
        pytermor.config \
    | postprocess_module

run --rmprefix "${PROJECT_NAME}". \
    --start-color 0 \
    --only "${PROJECT_NAME}" \
     --no-show \
    -o "${DEPENDS_PATH}/structure.svg"

run --rmprefix "${PROJECT_NAME}". \
    --start-color 0 \
    --show-cycle \
     --no-show \
    -o "${DEPENDS_PATH}/cycles.svg"

run --start-color 0 \
    --max-bacon 3 \
    --max-mod 0 \
    --max-cluster 100 \
    --keep \
     --no-show \
    -o "${DEPENDS_PATH}/imports-deep.svg"

#run --start-color 0 \
#    --max-bacon 3 \
#    --cluster \
#    --collapse \
#    -o "${DEPENDS_PATH}/imports-cross.svg"
#
#run --start-color 0 \
#    --max-bacon 12 \
#    --max-mod 1 \
#    --cluster \
#    --collapse \
#    -o "${DEPENDS_PATH}/imports-far.svg"
