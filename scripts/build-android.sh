#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -d "$project_root/.tooling/jdk17" ]]; then
  export JAVA_HOME="$project_root/.tooling/jdk17"
fi
if [[ -d "$project_root/.tooling/android-sdk" ]]; then
  export ANDROID_HOME="$project_root/.tooling/android-sdk"
fi
exec "$project_root/android/gradlew" -p "$project_root/android" assembleDebug lintDebug "$@"
