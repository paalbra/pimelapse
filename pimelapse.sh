#!/usr/bin/bash

ffmpeg -pattern_type glob -i '*_2.jpg' -an timelapse.mp4
