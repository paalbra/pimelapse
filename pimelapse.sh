#!/usr/bin/bash

ffmpeg -pattern_type glob -i 'output/*.jpg' -an -y pimelapse.mp4
