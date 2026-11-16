#!/bin/bash
# Runs all benchmarks of the paper in Docker, from the host: builds the image if it does not exist, then sets up the
# repository and runs all benchmarks (scripts/setup_repo_and_start_all_benchmarks.sh) in a container in the background.
#
# Usage: bash scripts/run_all_benchmarks_docker.sh <computer name>
#   computer name: stored with the results (column "computer" and file names of the CSVs), e.g., PC1
#
# Environment variables:
#   BENCHMARK_CORE  CPU core to which the benchmarks are pinned (default: 2)
#   BENCHMARK_NICE  niceness of the setup and the benchmarks (default: -20, the highest priority); negative values
#                   need the capability SYS_NICE, which the container gets; if it cannot be set, the benchmarks run
#                   with normal priority (see the first line of the log)
#   CONTAINER_NAME  name of the container (default: compare_benchmarks)
#
# Docker may need sudo. Progress: run_all_benchmarks.log (run, setup and benchmarks) and load.log (load average of the
# computer every minute: the computer should be idle apart from the benchmarks). Results: results/ and one CSV per
# benchmark in the repository root. The run takes about 8 to 10 hours. Case files that already have results are
# skipped, so after an interruption, remove the container (docker rm <name>) and start the script again.
set -e

if [ $# -ne 1 ]; then
  echo "Usage: bash scripts/run_all_benchmarks_docker.sh <computer name>"
  exit 1
fi
computer=$1
image=compare
name=${CONTAINER_NAME:-compare_benchmarks}
cd "$(dirname "$0")/.."

if ! docker image inspect "$image" > /dev/null 2>&1; then
  echo "Building the Docker image $image"
  docker buildx build -t "$image" .
fi
if docker container inspect "$name" > /dev/null 2>&1; then
  echo "A container $name exists already (still running or finished): remove it with docker rm -f $name"
  exit 1
fi

# runs in the container (variables are expanded there)
run='
exec > run_all_benchmarks.log 2>&1
niceness=$(nice -n "$BENCHMARK_NICE" nice 2> /dev/null)
echo "=== start $(date -Iseconds), computer $BENCHMARK_COMPUTER, core $BENCHMARK_CORE, niceness $niceness"
(while true; do echo "$(date +%H:%M:%S) $(cut -d" " -f1-3 /proc/loadavg)"; sleep 60; done) > load.log &
nice -n "$BENCHMARK_NICE" bash scripts/setup_repo_and_start_all_benchmarks.sh
echo "=== done $(date -Iseconds)"
'
docker run -d --name "$name" --cap-add=SYS_NICE \
  --mount type=bind,source="$PWD",target=/collision-comparison -w /collision-comparison \
  -e BENCHMARK_COMPUTER="$computer" -e BENCHMARK_CORE="${BENCHMARK_CORE:-2}" -e BENCHMARK_NICE="${BENCHMARK_NICE:--20}" \
  --entrypoint bash "$image" -c "$run" > /dev/null
echo "Started container $name. Progress: tail -f run_all_benchmarks.log"
