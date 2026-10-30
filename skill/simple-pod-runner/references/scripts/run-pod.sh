#!/bin/bash
# Schedule a simple pod, wait until it runs (or completes), print logs, delete it.
set -euo pipefail

IMAGE="public.ecr.aws/docker/library/nginx:latest"
NAME="simple-pod" TIMEOUT=120
while [[ $# -gt 0 ]]; do
  case "$1" in
    --image) IMAGE="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --timeout) TIMEOUT="${2%s}"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

RESULTS_DIR="${RESULTS_DIR:-/tmp/pkg-test-results}"; mkdir -p "$RESULTS_DIR"
LOG_FILE="$RESULTS_DIR/simple-pod-${NAME}-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "# logging to $LOG_FILE"

cleanup() { kubectl delete pod "$NAME" --ignore-not-found --wait=false; }
trap cleanup EXIT

kubectl apply -f - <<YAML
apiVersion: v1
kind: Pod
metadata:
  name: ${NAME}
  labels:
    app: ${NAME}
spec:
  restartPolicy: Never
  containers:
    - name: ${NAME}
      image: ${IMAGE}
      imagePullPolicy: Always
YAML

# Pass on Running (server-style image such as nginx) or Succeeded (batch-style image).
# Fail fast on Failed or a container waiting reason that indicates a pull/runtime error.
deadline=$(( $(date +%s) + TIMEOUT ))
while :; do
  phase=$(kubectl get pod "$NAME" -o jsonpath='{.status.phase}' 2>/dev/null || true)
  reason=$(kubectl get pod "$NAME" -o jsonpath='{.status.containerStatuses[0].state.waiting.reason}' 2>/dev/null || true)
  case "$phase" in
    Running|Succeeded)
      echo "PASS: pod ${NAME} pulled ${IMAGE} and ran (phase ${phase})."
      kubectl logs "$NAME" --tail=20 || true
      exit 0 ;;
    Failed) break ;;
  esac
  case "$reason" in
    ErrImagePull|ImagePullBackOff|CreateContainerError|CreateContainerConfigError|CrashLoopBackOff|InvalidImageName) break ;;
  esac
  (( $(date +%s) >= deadline )) && break
  sleep 3
done
echo "FAIL: pod ${NAME} did not run (phase '${phase}', reason '${reason}')." >&2
kubectl describe pod "$NAME" >&2 || true
exit 1
