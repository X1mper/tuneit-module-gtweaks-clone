#!/bin/bash

SCHEMA="org.gnome.desktop.wm.preferences"
KEY="button-layout"

get_layout() {
    gsettings get "$SCHEMA" "$KEY" | tr -d "'"
}

set_layout() {
    gsettings set "$SCHEMA" "$KEY" "$1"
}

get_button_side() {
    local layout=$(get_layout)
    local left="${layout%%:*}"
    [[ "$left" == *close* || "$left" == *minimize* || "$left" == *maximize* ]] && echo "false" || echo "true"
}

set_button_side() {
    local target_right="$1"
    local layout=$(get_layout)
    local left="${layout%%:*}"
    local right="${layout#*:}"

    local buttons=""
    for btn in close minimize maximize; do
        [[ "$layout" == *"$btn"* ]] && buttons="$buttons $btn"
    done

    local left_extras="" right_extras=""
    for item in ${left//,/ }; do
        [[ ! " close minimize maximize " =~ " $item " && -n "$item" ]] && left_extras="${left_extras:+$left_extras,}$item"
    done
    for item in ${right//,/ }; do
        [[ ! " close minimize maximize " =~ " $item " && -n "$item" ]] && right_extras="${right_extras:+$right_extras,}$item"
    done

    # Order: Windows (min,max,close) for right, macOS (close,min,max) for left
    local ordered=""
    if [[ "$target_right" == "true" ]]; then
        for btn in minimize maximize close; do
            [[ "$buttons" == *"$btn"* ]] && ordered="${ordered:+$ordered,}$btn"
        done
        set_layout "${left_extras}:${ordered}${right_extras:+,$right_extras}"
    else
        for btn in close minimize maximize; do
            [[ "$buttons" == *"$btn"* ]] && ordered="${ordered:+$ordered,}$btn"
        done
        set_layout "${left_extras:+$left_extras,}${ordered}:${right_extras}"
    fi
}

has_button() {
    [[ "$(get_layout)" == *"$1"* ]] && echo "true" || echo "false"
}

toggle_button() {
    local btn="$1" state="$2" side="$3"
    local layout=$(get_layout)
    local left="${layout%%:*}" right="${layout#*:}"

    if [[ "$state" == "true" ]]; then
        if [[ "$layout" != *"$btn"* ]]; then
            if [[ "$side" == "true" ]]; then
                set_layout "${left}:${right:+$right,}$btn"
            else
                set_layout "${left:+$left,}$btn:${right}"
            fi
            set_button_side "$side"
        fi
    else
        left=$(echo "$left" | sed "s/$btn//g; s/,,*/,/g; s/^,//; s/,$//")
        right=$(echo "$right" | sed "s/$btn//g; s/,,*/,/g; s/^,//; s/,$//")
        set_layout "${left}:${right}"
    fi
}

case "$1" in
    get_value)
        case "$2" in
            side) get_button_side ;;
            close|minimize|maximize) has_button "$2" ;;
        esac ;;
    set_value)
        case "$2" in
            side) set_button_side "$3" ;;
            close|minimize|maximize) toggle_button "$2" "$3" "$4" ;;
        esac ;;
esac
