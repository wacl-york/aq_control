#!/usr/bin/env bash
################################################################################
# run_control
#===============================================================================
# Define log file name for the data reading/writing program and start it from
# the right location.
################################################################################
WORKDIR="$(readlink -f "$(dirname "${0}")")"
LOGDIR="${WORKDIR}/logs"
LOGFILE="${LOGDIR}/control.log"
PYTHON=$(command -v python3)

cd "${WORKDIR}" || exit 1
${PYTHON} "${WORKDIR}/control.py" > "${LOGFILE}" 2>&1
