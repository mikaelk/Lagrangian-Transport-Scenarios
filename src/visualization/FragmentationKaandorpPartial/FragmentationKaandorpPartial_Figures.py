import settings
import numpy as np
import visualization.FragmentationKaandorpPartial.FragmentationKaandorpPartial_SizeSpectrumTime as FragmentationKaandorpPartial_SizeSpectrumTime


def run(scenario, figure_direc: str):
    shore_time_list = np.array([1, 20])
    lambda_frag_list = np.array([1, 10, 100, 200, 300, 388])

    FragmentationKaandorpPartial_SizeSpectrumTime.run(figure_direc=figure_direc, scenario=scenario, shore_time=20,
                                                      lambda_frag_list=lambda_frag_list, density=920)