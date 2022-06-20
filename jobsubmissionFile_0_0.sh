#!/bin/bash
#
#
#SBATCH --job-name=AdvDifOnly_y=2015__run=0_restart=0
#SBATCH --output=runOutput/AdvDifOnly_y=2015__run=0_restart=0.o%j
#SBATCH --mem-per-cpu=40G
#SBATCH --time=00:20:00
#
#
#
#
cd "/nethome/kaand004/Git_repositories/Lagrangian-Transport-Scenarios/"
python src/main.py -p 10 -v
