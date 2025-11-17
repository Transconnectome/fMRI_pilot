#!/usr/bin/env python3
"""
Generate image playlist CSV for NSD-style fMRI experiment using COCO dataset
Based on Natural Scenes Dataset experimental design
"""

import os
import csv
import random
import argparse
import numpy as np
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser(description="Generate NSD-style image playlist from COCO dataset")
    parser.add_argument("--coco_dir", type=str, default="/storage/bigdata/NSD_stimulus",
                        help="COCO dataset root directory")
    parser.add_argument("--output_csv", type=str, default="/scratch/connectome/seokjin14/fMRI_pilot/pilot_nsd/image_playlist.csv",
                        help="Output CSV file path")
    parser.add_argument("--n_sessions", type=int, default=1,
                        help="Number of sessions")
    parser.add_argument("--n_runs_per_session", type=int, default=12,
                        help="Number of runs per session (NSD uses 12)")
    parser.add_argument("--n_images_per_run", type=int, default=62,
                        help="Number of images per run (NSD uses 62: 750 trials / 12 runs)")
    parser.add_argument("--n_repetitions", type=int, default=3,
                        help="Number of times each image is presented (NSD uses 3)")
    parser.add_argument("--von_mises_ratio", type=float, default=0.6,
                        help="Ratio of von Mises distribution (NSD uses 0.6)")
    parser.add_argument("--von_mises_kappa", type=float, default=729.0,
                        help="Concentration parameter for von Mises (NSD uses 729)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    parser.add_argument("--use_train_only", action="store_true",
                        help="Use only training images (not validation)")
    return parser.parse_args()

def collect_coco_images(coco_dir, use_train_only=False):
    """Collect all COCO image paths"""
    train_dir = os.path.join(coco_dir, "train2017")
    val_dir = os.path.join(coco_dir, "val2017")

    images = []

    # Collect training images
    if os.path.exists(train_dir):
        train_images = [os.path.join(train_dir, f) for f in os.listdir(train_dir)
                       if f.endswith(('.jpg', '.png'))]
        images.extend(train_images)
        print(f"Found {len(train_images)} training images")

    # Collect validation images
    if not use_train_only and os.path.exists(val_dir):
        val_images = [os.path.join(val_dir, f) for f in os.listdir(val_dir)
                     if f.endswith(('.jpg', '.png'))]
        images.extend(val_images)
        print(f"Found {len(val_images)} validation images")

    print(f"Total images collected: {len(images)}")
    return images

def sample_repetition_interval(total_trials, von_mises_ratio=0.6, kappa=729.0, rng=None):
    """
    Sample repetition interval using mixture of von Mises and uniform distributions.

    Args:
        total_trials: Total number of trials available
        von_mises_ratio: Proportion of von Mises distribution (default 0.6 for NSD)
        kappa: Concentration parameter for von Mises (default 729 for NSD)
        rng: Random number generator

    Returns:
        interval: Number of trials between repetitions
    """
    if rng is None:
        rng = np.random

    # Decide which distribution to use
    if rng.random() < von_mises_ratio:
        # von Mises distribution (wrapped normal on circle)
        # Sample from von Mises centered at 0
        angle = rng.vonmises(0, kappa)
        # Map to [0, 1] range
        normalized = (angle + np.pi) / (2 * np.pi)
    else:
        # Uniform distribution
        normalized = rng.random()

    # Map to trial interval [1, total_trials]
    # Use exponential-like mapping to bias towards shorter intervals
    interval = int(normalized * total_trials) + 1
    interval = max(1, min(total_trials, interval))

    return interval

def generate_playlist(images, n_sessions, n_runs_per_session, n_images_per_run,
                     n_repetitions=3, von_mises_ratio=0.6, von_mises_kappa=729.0, seed=42):
    """
    Generate playlist with NSD-style repetition structure.

    Each unique image is presented n_repetitions times (default 3).
    The temporal spacing between repetitions follows a mixture of:
    - von Mises distribution (60%)
    - Uniform distribution (40%)

    Args:
        images: List of image paths
        n_sessions: Number of sessions
        n_runs_per_session: Number of runs per session
        n_images_per_run: Number of image presentations per run
        n_repetitions: Number of times each image is shown (default 3)
        von_mises_ratio: Ratio of von Mises distribution (default 0.6)
        von_mises_kappa: Concentration parameter for von Mises (default 729)
        seed: Random seed

    Returns:
        playlist: List of trial dictionaries
    """
    random.seed(seed)
    np.random.seed(seed)
    rng = np.random.RandomState(seed)

    total_trials = n_sessions * n_runs_per_session * n_images_per_run
    n_unique_images = total_trials // n_repetitions

    if len(images) < n_unique_images:
        raise ValueError(f"Not enough unique images! Need {n_unique_images}, but only have {len(images)}")

    print(f"\nGenerating playlist:")
    print(f"  Total trials: {total_trials}")
    print(f"  Unique images: {n_unique_images}")
    print(f"  Repetitions per image: {n_repetitions}")
    print(f"  von Mises ratio: {von_mises_ratio}")
    print(f"  von Mises kappa: {von_mises_kappa}")

    # Shuffle and select unique images
    random.shuffle(images)
    unique_images = images[:n_unique_images]

    # Create all trials as a flat list first
    all_trials = []
    trial_idx = 0

    for img_idx, img_path in enumerate(unique_images):
        # First presentation of this image
        first_trial = trial_idx
        all_trials.append({
            'trial_idx': trial_idx,
            'image_path': img_path,
            'image_id': img_idx,
            'repetition_num': 0,
            'is_repeat': 0
        })
        trial_idx += 1

        # Schedule repetitions
        for rep in range(1, n_repetitions):
            # Sample interval from first presentation
            max_interval = total_trials - first_trial - (n_repetitions - rep)
            if max_interval < 1:
                interval = 1
            else:
                interval = sample_repetition_interval(max_interval, von_mises_ratio,
                                                      von_mises_kappa, rng)

            repeat_trial = first_trial + interval
            # Ensure we don't exceed total trials
            repeat_trial = min(repeat_trial, total_trials - (n_repetitions - rep))

            all_trials.append({
                'trial_idx': repeat_trial,
                'image_path': img_path,
                'image_id': img_idx,
                'repetition_num': rep,
                'is_repeat': 1
            })

    # Sort by trial index to get temporal order
    all_trials.sort(key=lambda x: (x['trial_idx'], x['image_id']))

    # Assign to sessions and runs
    playlist = []
    trial_counter = 0

    for session in range(1, n_sessions + 1):
        for run in range(1, n_runs_per_session + 1):
            for order in range(1, n_images_per_run + 1):
                if trial_counter < len(all_trials):
                    trial = all_trials[trial_counter]
                    playlist.append({
                        'session': session,
                        'run': run,
                        'order': order,
                        'image_path': trial['image_path'],
                        'is_repeat': trial['is_repeat'],
                        'image_id': trial['image_id'],
                        'repetition_num': trial['repetition_num']
                    })
                    trial_counter += 1

    return playlist

def write_csv(playlist, output_path):
    """Write playlist to CSV file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['session', 'run', 'order', 'image_path',
                                               'is_repeat', 'image_id', 'repetition_num'])
        writer.writeheader()
        writer.writerows(playlist)

    print(f"\nPlaylist saved to: {output_path}")
    print(f"Total entries: {len(playlist)}")

    # Print statistics
    n_repeats = sum(1 for x in playlist if x['is_repeat'] == 1)
    n_unique = len(set(x['image_path'] for x in playlist))
    print(f"Unique images: {n_unique}")
    print(f"First presentations: {len(playlist) - n_repeats}")
    print(f"Repeat presentations: {n_repeats}")

def main():
    args = get_args()

    print("=" * 60)
    print("NSD-style Image Playlist Generator")
    print("=" * 60)
    print(f"COCO directory: {args.coco_dir}")
    print(f"Output CSV: {args.output_csv}")
    print(f"Sessions: {args.n_sessions}")
    print(f"Runs per session: {args.n_runs_per_session}")
    print(f"Images per run: {args.n_images_per_run}")
    print(f"Repetitions per image: {args.n_repetitions}")
    print(f"von Mises ratio: {args.von_mises_ratio}")
    print(f"von Mises kappa: {args.von_mises_kappa}")
    print(f"Random seed: {args.seed}")
    print("=" * 60)

    # Collect COCO images
    print("\nCollecting COCO images...")
    images = collect_coco_images(args.coco_dir, args.use_train_only)

    # Generate playlist
    print("\nGenerating playlist...")
    playlist = generate_playlist(
        images,
        args.n_sessions,
        args.n_runs_per_session,
        args.n_images_per_run,
        args.n_repetitions,
        args.von_mises_ratio,
        args.von_mises_kappa,
        args.seed
    )

    # Write to CSV
    write_csv(playlist, args.output_csv)

    print("\nPlaylist generation complete!")
    print("\nTo run the experiment, use:")
    print(f"python nsd_image_experiment.py \\")
    print(f"  --sub_id 01 \\")
    print(f"  --session 1 \\")
    print(f"  --image_csv_path {args.output_csv}")

if __name__ == "__main__":
    main()
