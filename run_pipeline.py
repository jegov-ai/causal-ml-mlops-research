

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

steps = [
    "generate_data.py",
    "validate_data.py",
    "train_causal_model.py",
    "log_experiment.py",
    "optimize_product.py"
]

print("STARTING CAUSAL ML + MLOPS PIPELINE", flush=True)

for step in steps:
    print("\nRunning:", step, flush=True)

    subprocess.run(
        [sys.executable, str(ROOT / step)],
        cwd=ROOT,
        check=True
    )

print("\nFULL PIPELINE COMPLETED SUCCESSFULLY!")
