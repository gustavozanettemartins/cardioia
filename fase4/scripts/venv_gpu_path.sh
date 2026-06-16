#!/usr/bin/env bash
# Auto-executado ao ativar ~/cardioia-venv no WSL2.
NVIDIA_LIBS=$(python - << 'PY'
import glob
import os
import site

sp = site.getsitepackages()[0]
paths = glob.glob(os.path.join(sp, "nvidia", "*", "lib"))
print(":".join(paths))
PY
)

export LD_LIBRARY_PATH="/usr/lib/wsl/lib:${NVIDIA_LIBS}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
