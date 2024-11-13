#!/usr/bin/env bash

# TODO: detect incomplete or corrupt downloaded client files

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_DIR=${SCRIPT_DIR} # $(dirname ${SCRIPT_DIR})
OUTPUT_DIR=${PROJECT_DIR}/results
TEMP_DIR=/tmp
# populated by okd in prod
# MANIFEST_FILE_DIR=${PROJECT_DIR}/../temp__client_manifest_files
RESOURCES_DIR=${PROJECT_DIR}/resources

FETCHMANIFESTS="${1}"

suniq() {
    sort | uniq
}

fetch_manifests() {
    echo "fetching manifests"
    mkdir -p ${OUTPUT_DIR}/manifests
    CURTIME=$(date +%s)
    for f in $(cat ${RESOURCES_DIR}/client_manifest_urls.txt); do
        FNAME=${f##*/}
        curl --connect-timeout 5 \
             --max-time 10 \
             --retry 5 \
             --retry-delay 0 \
             --retry-max-time 40 \
             -o ${OUTPUT_DIR}/manifests/${FNAME} \
            "${f}?${CURTIME}" 
    done
}

extract_client_filenames_from_manifests() {

    echo "extract_client_filenames_from_manifests"

    pushd ${OUTPUT_DIR}/manifests >/dev/null 2>&1

    grep -EIo '"[A-Za-z0-9_.-]+\.zip\.[A-Za-z0-9_.-]+"' * | \
        grep -v '.zip.vz' | \
        suniq > ${TEMP_DIR}/client_manifest_filenames.txt;
    
    cat ${TEMP_DIR}/client_manifest_filenames.txt | \
        cut -d ':' -f 2 | \
        tr -d '"' | \
        suniq > ${OUTPUT_DIR}/client_manifest_filenames_clean.txt;
    
    popd >/dev/null 2>&1

}

download_client_files() {

    echo "download_client_files"

    mkdir -p ${MANIFEST_FILE_DIR}

    for MFNAME in $(cat ${OUTPUT_DIR}/client_manifest_filenames_clean.txt); do
    
        if [ ! -f ${MANIFEST_FILE_DIR}/${MFNAME} ]; then
            echo "redownloading ${MFNAME} for some reason"
            curl -L --connect-timeout 5 \
                    --max-time 10 \
                    --retry 5 \
                    --retry-delay 0 \
                    --retry-max-time 40 \
                    -o ${MANIFEST_FILE_DIR}/${MFNAME} \
                    https://cdn.steamstatic.com/client/${MFNAME}
        fi

    done
}

handlemanifests() {

    echo "handlemanifests" 
    if [[ "x${FETCHMANIFESTS}" == "x" ]]; then
        fetch_manifests
    fi
    extract_client_filenames_from_manifests
    download_client_files

    echo "process_client_manifests.py"
    export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH}"
    python3 ${PROJECT_DIR}/scripts/process_client_manifests.py ${TEMP_DIR}/client_manifest_filenames.txt ${MANIFEST_FILE_DIR} ${OUTPUT_DIR}

}


handlemanifests

COMMIT_MESSAGE=$(python3 ${PROJECT_DIR}/scripts/create_commit_message.py) && export COMMIT_MESSAGE