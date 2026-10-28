

import subprocess
import sys

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
        [sys.executable, step],
        check=True
    )

print("\nFULL PIPELINE COMPLETED SUCCESSFULLY!")
