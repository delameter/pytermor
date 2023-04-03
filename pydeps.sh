#------------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]                           -
# (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>                          -
# Licensed under GNU Lesser General Public License v3.0                       -
#------------------------------------------------------------------------------

PROJECT_NAME="${1:?Project name required}"
DEPENDS_PATH="${2:?Output path required}"

run() {
    # args: [cmd-option]...
    export PT_ENV=build
    set -- ./.invoke pydeps "${PROJECT_NAME}" "$@"
    echo "$*" >&2
    "$@"
}

run --rmprefix "${PROJECT_NAME}". \
    --only "${PROJECT_NAME}" \
    --no-output \
    --rankdir TB \
    --show-dot \
    -xx pytermor pytermor._version \
    | tee "${DOCS_IN_PATH}/_generated/module.dot"

run --rmprefix "${PROJECT_NAME}". \
    --start-color 120 \
    --only "${PROJECT_NAME}" \
     --no-show \
    -o "${DEPENDS_PATH}/structure.svg"

run --rmprefix "${PROJECT_NAME}". \
    --start-color 120 \
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
