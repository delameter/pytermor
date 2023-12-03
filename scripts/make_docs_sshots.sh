#!/bin/bash
# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
# Docs terminal screenshot generator
declare -ir PP=7
declare -ar HEADER_STROKES=(1)

declare -ir CHAR_W_PX=9
declare -ir CHAR_H_PX=21
declare -ir MIN_RESULT_W_PX=800
declare -ir MAX_RESULT_H_PX=1000
declare -ir OFFSET_X_PX=0
declare -ir OFFSET_Y_PX=0
declare -ir PADDING_X_CH=1
# values are adjusted for:
# -----------------------------------------
# TERMINAL APP  GNOME Terminal / Terminator
#    TEXT FONT  Iose7ka Terminal Medium 12
#  WINDOW SIZE  fullscreen 1080p
# -----------------------------------------

function fstat() { stat -Lc $'%10s  %n' "$@" | es7s exec hilight - ; }
function min() { [[ $(( ${1:?} )) -lt $(( ${2:?} )) ]] && echo $1 || echo $2 ; }
function max() { [[ $(( ${1:?} )) -gt $(( ${2:?} )) ]] && echo $1 || echo $2 ; }
function dcu() { sed -Ee 's/\x1b\[[0-9;:]*[A-Za-z]//g; s/\xe2\x80\x8e//g'; }
function checkdep() {
  command -v "${1:?}" &>/dev/null && return
  echo "ERROR: ${2:-$1} not installed, unable to proceed"
  exit 1
}
function measure_width() {
  # reads stdin
  { while read -r line ; do
      wc <<< "$line" -m
    done < <(normalize | dcu) ;
  } | sort -nr | head -1 ;
}
function normalize() {
  sed -Ee 's/.+\x1b\[2K//;'  # emulate ERASE IN LINE 2 application
}

# ------------------
__help() {
  __SELF="$(basename "$0" | sed -Ee 's/\..+$//')"
  echo "USAGE: $__SELF [-a] [-y] [OUTPUT_DIR] [PYTHON_PATH]"
  echo
  echo "  Render docs screenshots, place into OUTPUT_DIR. If specified,"
  echo "  use PYTHON_PATH as custom path to python interpreter. Both"
  echo "  can be provided in a format relative to current working dir."
  echo
  echo "OPTIONS"
  echo "  -a, --all    Do not skip already existing artifacts."
  echo "  -y, --yes    Write artifacts without user confirmation."
}
__pytermor() {
    local OPT_ALL=
    local OPT_YES=

    while getopts ay-: OPT; do
        if [ "$OPT" = "-" ]; then
            OPT="${OPTARG%%=*}"
            OPTARG="${OPTARG#$OPT}"
            OPTARG="${OPTARG#=}"
        fi
        # shellcheck disable=SC2214
        case "$OPT" in
                 a|all) OPT_ALL=true ;;
                 y|yes) OPT_YES=true ;;
                  help) __help && return 0 ;;
                 ??*|?) echo "Invalid option -${OPTARG:-"-"$OPT}" && __help && return 0 ;;
        esac
    done
    shift $((OPTIND-1))

    # shellcheck disable=SC2086
    function invoke() {
      # args: cmd [opts...]
      export ES7S_PADBOX_HEADER="./$(basename "$execpath") $*"
      padbox "$execpath" "$@"
    }
    function p1() {
      local color=A09CB5
      invoke examples/approximate.py $color
      invoke examples/approximate.py $color -R | sed -Ee 2,3d
      invoke examples/approximate.py $color -H | sed -Ee 2,3d
    }
    function p2() {
      invoke examples/list_named_rgb.py |
        cutl 2449 2464 "s/^\s+//;"
    }
    function p3() {
      COLUMNS=100 \
        invoke examples/list_named_rgb.py grid 16 5 |
        cutl 2257 2274 "s/$/\xa0/;"
    }
    function p4() {
      invoke examples/render_benchmark.py |
        cutl 43 60 "s/(\|[^|]+)\|[^|]+/\1/g"
    }
    function p5() {
      PYTERMOR_FORCE_OUTPUT_MODE=true_color \
        invoke examples/terminal_color_mode.py |
        cutl 2 19
    }
    function p6() {
      PYTERMOR_FORCE_OUTPUT_MODE=true_color \
        COLUMNS=120 \
        invoke examples/tone_neighbours.py 106020 |
        cutl 2 23
    }
    function p7() {
      PYTERMOR_FORCE_OUTPUT_MODE=true_color \
        COLUMNS=160 \
        invoke examples/list_named_rgb.py grid 1 |
        cutl '' '' "s/^|$/\xa0/g;"
    }
    function cutl() {
      # args: [start_lineno], [end_lineno] [extra_expr]
      local start_lineno="${1:+2,${1}d; 1a...}"
      local end_lineno="${2:+$(($2+1)),\$d; ${2}a...}"
      local extra_expr="${3:-;}"
      sed -Ee "$start_lineno" -e "$end_lineno" -e "$extra_expr"
    }
    function get_extra_strokes() {
        local fnum="${1:?}"
        [[ $fnum == 1 ]] && echo 1 11 12 20 21
        echo "${HEADER_STROKES[@]}"
    }

    function measure() {
      # arg: filepath
      local w_ch=$(measure_width < ${1:?})
      local h_ch=$(wc -l < ${1:?})
      echo "measured (ch): $w_ch $h_ch" >&2

      local result_w_px=$(max $MIN_RESULT_W_PX $(( CHAR_W_PX * (w_ch + 2*PADDING_X_CH) )) )
      local result_h_px=$(min $MAX_RESULT_H_PX $(( CHAR_H_PX * h_ch )) )
      echo "measured (px): $result_w_px $result_h_px" >&2

      echo "$OFFSET_X_PX,$OFFSET_Y_PX,$result_w_px,$result_h_px"
    }

    # shellcheck disable=SC2054,SC2206
    function pp() {
        # args: imgin imgout [header_hch...]

        local -a cmds=()
        for h in ${*:3} ; do
          local -i header_hpx=$(( h * CHAR_H_PX + 1 ))
          cmds+=(polygon 2,0,$header_hpx,100%,$header_hpx,1,66)
        done

        cmds+=(
          to_rgba
          fx_frame 0,100,0,100,0,0,255,255,255,255,1,100,100,100,255
          expand_x 15,0
          expand_y 15,0
          crop 0,15,100%,100%,0
          drop_shadow 5,5,2.5,0,0,0
          output "${2:?}"
          display_rgba
        )

        gmic "${1:?}" "${cmds[@]}"
    }

    local outdir=$(realpath "${1:-./docs/_generated/term-output}")
    local execpath=$(realpath "${2:-./run-cli}")

    local tmpout=/tmp/pbc-out
    local tmpimg=/tmp/pbc.png
    local tmpimgpp=/tmp/pbcpp.png
    local promptyn=$'\x1b[m Save? \x1b[34m[y/N/^C]\x1b[94m>\x1b[m '

    [[ -d "$outdir" ]] || { echo "ERROR: Dir does not exist: ${outdir@Q}" && exit 1 ; }
    [[ -x "$execpath" ]] || execpath=

    export ES7S_PADBOX_PAD_Y=0
    export ES7S_PADBOX_PAD_X=$PADDING_X_CH
    export ES7S_PADBOX_NO_CLEAR=true
    export PAGER=

    for fn in $(seq $PP) ; do
        local imgout="$outdir/example$(printf %03d $fn).png"
        local prompt=$(printf '\x1b[33m[\x1b[93;1m%2d\x1b[;33m/\x1b[1m%2d\x1b[;33m]\x1b[m' "$fn" $PP)

        if [[ ! $OPT_ALL ]] ; then
          # shellcheck disable=SC2046,SC2005
          [[ -f "$imgout" ]] \
            && echo "$prompt Skipping existing: $(echo $(basename -a "$imgout"))" \
            && continue
        fi

        clear
        "p$fn" |& tee $tmpout

        echo "Preparing to take a screenshot..."
        sleep 0.5
        scrot -o "$tmpimg" -a "$(measure "$tmpout")"  #-e 'xdg-open $f'

        # shellcheck disable=SC2046,SC2086
        pp "$tmpimg" "$tmpimgpp" $(get_extra_strokes $fn)

        if [[ ! $OPT_YES ]] ; then
          read -r -n1 -p"$prompt$promptyn" yn ; echo
        else yn=y ; fi
        if [[ $yn =~ [Yy] ]] ; then
            cp -v "$tmpimgpp" "$imgout"
            fstat "$imgout"
        fi
    done
}

checkdep gmic
checkdep padbox es7s
(__pytermor "$@")
