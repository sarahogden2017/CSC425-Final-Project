#!/usr/bin/env python3
"""
Split image dataset into train/test (and optional val) folders.

Usage examples (Windows cmd):
    python scripts/split_dataset.py --src data --dst dataset_out --train-ratio 0.8
    python scripts/split_dataset.py --src data --dst dataset_out --train-ratio 0.7 --val-ratio 0.15 --move

The script expects `--src` to contain class subdirectories, e.g.:
  data/rose/*.jpg
  data/tulip/*.jpg

It will create `--dst` with `train/`, `test/`, and optional `val/` subfolders, preserving class names.
"""
import argparse
import os
import random
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}


def is_image_file(p: Path) -> bool:
    return p.suffix.lower() in IMAGE_EXTENSIONS


def gather_class_files(src_dir: Path):
    classes = {}
    for child in sorted(src_dir.iterdir()):
        if child.is_dir():
            files = [p for p in child.iterdir() if p.is_file() and is_image_file(p)]
            if files:
                classes[child.name] = files
    return classes


def make_output_dirs(dst: Path, splits, class_names):
    for s in splits:
        for c in class_names:
            (dst / s / c).mkdir(parents=True, exist_ok=True)


def split_and_copy(classes, dst: Path, train_ratio: float, val_ratio: float, seed: int, move: bool, dry_run: bool):
    random.seed(seed)
    splits = ['train', 'test']
    if val_ratio and val_ratio > 0:
        splits = ['train', 'val', 'test']

    make_output_dirs(dst, splits, classes.keys())

    summary = {s: {c: 0 for c in classes.keys()} for s in splits}

    for cls, files in classes.items():
        files = list(files)
        random.shuffle(files)
        n = len(files)
        if val_ratio and val_ratio > 0:
            n_val = int(n * val_ratio)
        else:
            n_val = 0
        n_train = int(n * train_ratio)
        # Ensure at least 1 in test if possible
        n_test = n - n_train - n_val
        if n_test <= 0 and n > 0:
            # move one to test if train used all
            n_test = 1
            if n_train > 0:
                n_train -= 1
            elif n_val > 0:
                n_val -= 1

        idx = 0
        ranges = []
        ranges.append(('train', files[idx: idx + n_train])); idx += n_train
        if n_val > 0:
            ranges.append(('val', files[idx: idx + n_val])); idx += n_val
        ranges.append(('test', files[idx:]))

        for split_name, group in ranges:
            for src_path in group:
                dst_path = dst / split_name / cls / src_path.name
                if dry_run:
                    summary[split_name][cls] += 1
                    continue
                if move:
                    shutil.move(str(src_path), str(dst_path))
                else:
                    shutil.copy2(str(src_path), str(dst_path))
                summary[split_name][cls] += 1

    return summary


def print_summary(summary):
    print('\nSplit summary:')
    totals = {}
    for split, classes in summary.items():
        s_total = sum(classes.values())
        totals[split] = s_total
        print(f'  {split}: {s_total} images')
    print('Per-class counts:')
    for cls in next(iter(summary.values())).keys():
        counts = [summary[s][cls] for s in summary.keys()]
        print(f'  {cls}: ' + ', '.join(f'{s}={c}' for s, c in zip(summary.keys(), counts)))


def parse_args():
    p = argparse.ArgumentParser(description='Split image dataset into train/test (and optional val)')
    p.add_argument('--src', required=True, help='Source directory with class subfolders')
    p.add_argument('--dst', required=True, help='Destination directory to create train/test (and val)')
    p.add_argument('--train-ratio', type=float, default=0.8, help='Fraction for training (0-1)')
    p.add_argument('--val-ratio', type=float, default=0.0, help='Fraction for validation (0-1). If >0, val is created.')
    p.add_argument('--seed', type=int, default=1337, help='Random seed')
    p.add_argument('--move', action='store_true', help='Move files instead of copying')
    p.add_argument('--dry-run', action='store_true', help="Don't copy/move, just print what would happen")
    p.add_argument('--extensions', nargs='*', default=None, help='Optional list of extensions to include (e.g. .jpg .png)')
    return p.parse_args()


def main():
    args = parse_args()
    src = Path(args.src)
    dst = Path(args.dst)

    if not src.exists() or not src.is_dir():
        print(f'Error: src {src} not found or not a directory')
        return

    if args.extensions:
        global IMAGE_EXTENSIONS
        IMAGE_EXTENSIONS = set(e.lower() if e.startswith('.') else ('.' + e.lower()) for e in args.extensions)

    classes = gather_class_files(src)
    if not classes:
        print('No class subfolders with images found in src')
        return

    print('Found classes and image counts:')
    for c, files in classes.items():
        print(f'  {c}: {len(files)}')

    if args.dry_run:
        print('\nDry run: no files will be copied or moved')

    summary = split_and_copy(classes, dst, args.train_ratio, args.val_ratio, args.seed, args.move, args.dry_run)
    print_summary(summary)


if __name__ == '__main__':
    main()
