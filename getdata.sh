#!/bin/bash
curl -L -o ~/data/flowers-dataset.zip\
  https://www.kaggle.com/api/v1/datasets/download/imsparsh/flowers-dataset

unzip ~/data/flowers-dataset.zip -d ~/data/labeled/flowers-dataset
rm ~/data/flowers-dataset.zip