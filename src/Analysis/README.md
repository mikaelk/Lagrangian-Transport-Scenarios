# Analysis

This directory contains a number of files, each containing a standardized function for post-processing of the parcels
output.

The files (and corresponding functions) contained within this directory are:
- `parcels_to_basicstatistics.py`: Saves some basic statistics for a given simulation, such as max/min/mean/std values
of various particle characteristics.
- `parcels_to_concentrations.py`: Computes the horizontal concentration, both averaged over the entire length of the
simulation and for each simulation year.
- `parcels_to_max_distance.py`: Computes the maximum distance each particle is removed from the model coastline throughout
a simulation. Note: this analysis should only be done if the particle simulation tracks the distance to shore throughout
the parcels simulation.
- `parcels_to_timeseries.py`: Computes the beached/floating/seabed fraction over time.
- `parcels_to_timeslices.py`: Splits up the parcels files into timeslices, where each file corresponds to all the
particles in the simulation at a given timepoint. This allows for easier loading of particles data in e.g. making
animations, as for large simulations loading all particle trajectory data is too much for the computer RAM.
- `parcels_to_vertical_concentration.py`: Computes vertical concentration profiles.