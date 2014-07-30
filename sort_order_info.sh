#!/usr/bin/env bash
echo 'city,state,population,population density,walk,transit,bike' > city-info.txt
python census.py | tee census-info.txt | python walkscore.py >> city-info.txt
