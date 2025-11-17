#!/bin/bash

# NSD-style fMRI Image Presentation Experiment
# Usage: ./run_experiment.sh [subject_id] [session_number]

# Default values
SUB_ID=${1:-"01"}
SESSION=${2:-1}

# Paths
SCRIPT_DIR="/scratch/connectome/seokjin14/fMRI_pilot/pilot_nsd"
PYTHON_BIN="/home/connectome/seokjin14/.conda/envs/py39/bin/python"
EXPERIMENT_SCRIPT="${SCRIPT_DIR}/nsd_image_experiment.py"
IMAGE_CSV="${SCRIPT_DIR}/image_playlist.csv"
OUTPUT_DIR="${SCRIPT_DIR}/nsd_outputs"

# Set Python environment
export PATH="/home/connectome/seokjin14/.conda/envs/py39/bin:$PATH"

# Run experiment
cd "$SCRIPT_DIR"
"$PYTHON_BIN" "$EXPERIMENT_SCRIPT" \
  --sub_id "$SUB_ID" \
  --session "$SESSION" \
  --image_csv_path "$IMAGE_CSV" \
  --output_dir "$OUTPUT_DIR"

echo ""
echo "Experiment finished!"
echo "Results saved in: $OUTPUT_DIR/sub-${SUB_ID}/ses-$(printf '%02d' $SESSION)/"
