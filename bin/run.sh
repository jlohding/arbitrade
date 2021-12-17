#!/bin/bash

while getopts a:d: flag
do
    case "${flag}" in
        a) assets=${OPTARG};;
        d) date=${OPTARG};;
    esac
done

timeout_wrapper() {
    while timeout 120s python ../src/arbitrade/__main__.py -a "${assets}" -d "${date}"; [ $? -eq 124 ]
    do
    echo "timed out: kill and try again"
    timeout_wrapper
    done
    echo "executed successfully"
}

timeout_wrapper
