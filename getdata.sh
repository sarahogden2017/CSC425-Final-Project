#!/bin/bash
# Download both datasets
# Dataset 1: 🌸 | Flowers (https://www.kaggle.com/datasets/l3llff/flowers)
curl -L -o ./data/flowers.zip\
  https://www.kaggle.com/api/v1/datasets/download/l3llff/flowers
unzip ./data/flowers.zip -d ./data/labeled/flowers
rm ./data/flowers.zip
# Dataset 2: National Flowers
curl -L -o ./data/national_flowers.zip\
  https://www.kaggle.com/api/v1/datasets/download/shahidulugvcse/national-flowers
unzip ./data/national_flowers.zip -d ./data/labeled/national_flowers
rm ./data/national_flowers.zip

# Merge folders of the same flower type
mkdir ./data/labeled/our_flowers
cp -r ./data/labeled/flowers/flowers/* ./data/labeled/our_flowers/
cp -r ./data/labeled/national_flowers/flowerdataset/test/* ./data/labeled/our_flowers/
cp -r ./data/labeled/national_flowers/flowerdataset/train/* ./data/labeled/our_flowers/
# Lowercase all folder names
for f in ./data/labeled/our_flowers/*; do
  mv "$f" "$(dirname "$f")/$(basename "$f" | tr 'A-Z' 'a-z')"
done
# Print number of images per flower type
echo "Number of images per flower type before duplicates removal:"
for d in ./data/labeled/our_flowers/*; do
  if [ -d "$d" ]; then
    count=$(find "$d" -type f | wc -l)
    echo "$(basename "$d"): $count images"
  fi
done
# Remove duplicates
for d in ./data/labeled/our_flowers/*; do
  if [ -d "$d" ]; then
    find "$d" -type f -exec md5sum "{}" + | sort | uniq -w32 -d | awk '{print substr($0, index($0,$2))}' | while read -r file; do
      if [ -f "$file" ]; then
        rm "$file"
      fi
    done
  fi
done
# Print number of images per flower type after duplicates removal
echo "Number of images per flower type after duplicates removal:"
for d in ./data/labeled/our_flowers/*; do
  if [ -d "$d" ]; then
    count=$(find "$d" -type f | wc -l)
    echo "$(basename "$d"): $count images"
  fi
done
# Clean up
rm -rf ./data/labeled/flowers
rm -rf ./data/labeled/national_flowers
cp -r ./data/labeled/our_flowers/* ./data/labeled/
rm -rf ./data/labeled/our_flowers
echo "Datasets downloaded and merged successfully."