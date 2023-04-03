#!/bin/bash
#------------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]                           -
# (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>                          -
# Licensed under GNU Lesser General Public License v3.0                       -
#------------------------------------------------------------------------------
declare FILENAME=CHANGES.rst

printf '\n%10s%s%10s\n' '' 'CHANGELIST AUTOUPDATER' '' | tr ' ' =
cp $FILENAME $FILENAME.bak

mapfile < <(grep -oEnm1 '^\.\. <@pending(:[a-f0-9]+)?' $FILENAME.bak | cut -f1,3 -d: | tr -d ' .' | tr : $'\n')
declare lineno=$(tr -d '\n' <<< "${MAPFILE[0]}" | sed -Ee '/[0-9]+/!d')
declare last_commit=$(tr -d '\n' <<< "${MAPFILE[1]}" | sed -Ee '/[0-9a-f]+/!d')
declare cur_commit=$(git show --format=%h | head -1)

[[ -z $lineno ]] || [[ -z $last_commit ]] || [[ -z $cur_commit ]] && \
   echo "ERROR: incomplete data ('$lineno' '$cur_commit' '$last_commit')" && \
   exit 1
[[ $cur_commit == "$last_commit" ]] && \
    echo "No changes detected" && \
    exit 0

echo "Processing ${last_commit} -> ${cur_commit}"
: > $FILENAME
{
    head -n $((lineno-2)) $FILENAME.bak  # skip trailing newline and <@> instruction
    {
        git log "${last_commit}..${cur_commit}" --reverse --pretty='%B' | \
            sed -Ee '/^\s*$/d; s/^([^A-Z]*)([A-Z]+):?/- |\2|/; '
        echo
        echo ".. <@pending:${cur_commit}>"
    } | tee /dev/stderr 2> >(sed -Ee 's/^/ >> /' >&2)

    tail -n +$((lineno+1)) $FILENAME.bak

} >> $FILENAME

echo "DONE" && exit
