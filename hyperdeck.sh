#!/bin/bash

function list_disk() {
nc -w 1 10.1.12.201 9993 <<EOF
disk list
EOF
}

function transport_info() {
nc -w 1 10.1.12.201 9993 <<EOF
transport info
EOF
}

function clips_clear() {
nc -w 1 10.1.12.201 9993 <<EOF
clips clear
EOF
}

function clips_add() {
nc -w 1 10.1.12.201 9993 <<EOF
clips add: name: $1
EOF
}

function play() {
nc -w 1 10.1.12.201 9993 <<EOF
play: loop: true
EOF
}

function info() {
nc -w 1 10.1.12.201 9993 <<EOF
clips get
EOF
}

function clips_get() {
nc -w 1 10.1.12.201 9993 <<EOF
clips get
EOF
}


function add() {
    local clip_playing=$(clips_get | grep "^1:" | awk '{print $2}')
    echo "clip_playing: $clip_playing"
    local disklist=$(list_disk)
    #echo "list disk: $disklist"
    echo $disklist | grep $clip_playing | awk '{print $0}'
    local current_format=$(echo $disklist | grep $clip_playing) #| awk '{print $4}')
    echo "current_format: $current_format"
    local clip_info=$(echo $disklist | awk '/'^$1'/ {print $0}')
    echo "clip_info: $clip_info"
    local clip_format=$(echo $clip_info | awk '{print $4}')
    echo "clip_format: $clip_format"

    if [ "$current_format" != "$clip_format" ]; then
    echo "Transport format is not $clip_format but $current_format"
    fi
}

function add_clip() {
    local transport_info=$(transport_info | awk '/video format:/ {print $3}')
    local clip_info=$(list_disk | awk '/'^$1'/ {print $0}')
    local clip_format=$(echo $clip_info | awk '{print $4}')
    # if [ "$transport_info" != "$clip_format" ]; then
    #     echo "Transport format is not $clip_format but $transport_info"
    # fi
    local clip_name=$(echo $clip_info | awk '{print $1}')
    add=$(clips_add $clip_name)
    play
}
#function add_clip() {
#    local transport_info=$(transport_info | awk '/^video format:/ {print $3}' | xargs | tr -d '\r')
#    local clip_info=$(list_disk | awk '/^'$1'/ {print $0}' | xargs)
#    local clip_format=$(echo $clip_info | awk '{print $4}' | xargs)
#
#    echo "DEBUG: transport_info='$transport_info'"
#    echo "DEBUG: clip_info='$clip_info'"
#    echo "DEBUG: clip_format='$clip_format'"
#
#    # Show ASCII values to identify any hidden characters
#    echo "DEBUG: transport_info ASCII values:"
#    printf '%s' "$transport_info" | od -An -t dC
#    echo "DEBUG: clip_format ASCII values:"
#    printf '%s' "$clip_format" | od -An -t dC
#
#    if [ "$transport_info" != "$clip_format" ]; then
#        echo "Transport format is not $clip_format but $transport_info"
#        echo "Use -p \$CLIP_ID to force-play"
#        exit 1
#    fi
#    local clip_name=$(echo $clip_info | awk '{print $2}')
#
#    add=$(clips_add $clip_name)
#}
#function add_clip() {
#    local transport_info=$(transport_info | awk '/^video format:/ {print $3}')
#    local clip_info=$(list_disk | awk '/'^$1'/ {print $0}')
#    local clip_format=$(echo $clip_info | awk '{print $4}')
#    if [ "$transport_info" != "$clip_format" ]; then
#        echo "Transport format is not $clip_format but $transport_info"
#        echo "Use -p \$CLIP_ID to force-play"
#        exit 1
#    fi
#    local clip_name=$(echo $clip_info | awk '{print $2}')
#
#    add=$(clips_add $clip_name)
#}
#
function play_clip() {
    local transport_info=$(transport_info | awk '/video format:/ {print $3}')
    local clip_info=$(list_disk | awk '/'^$1'/ {print $0}')
    local clip_format=$(echo $clip_info | awk '{print $4}')
    # if [ "$transport_info" != "$clip_format" ]; then
    #     echo "Transport format is not $clip_format but $transport_info"
    # fi
    local clip_name=$(echo $clip_info | awk '{print $2}')

    clear=$(clips_clear)
    add=$(clips_add $clip_name)
    play
}

while getopts zitld:p:a: flag
do
    case "${flag}" in
        a) add_clip ${OPTARG};;
        l) list_disk;;
        d) disk=${OPTARG};;
        p) play_clip ${OPTARG};;
        t) transport_info;;
        i) info;;
        z) add;;
        n) play;;
    esac
done

#list_disk
