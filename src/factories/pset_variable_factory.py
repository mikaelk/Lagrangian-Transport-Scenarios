import numpy as np
import settings as settings


class PsetVariableFactory:
    @staticmethod
    def initialize_variable_dict_from_varlist(var_list: list, start_files: dict) -> dict:
        beach = True if "beach" in var_list else False
        age = True if "age" in var_list else False
        prox = True if "prox" in var_list else False
        size = True if "size" in var_list else False
        rho_plastic = True if 'rho_plastic' in var_list else False
        return PsetVariableFactory.initialize_variable_dict(start_files=start_files, beach=beach, age=age, prox=prox,
                                                            size=size, rho_plastic=rho_plastic)


    @staticmethod
    def initialize_variable_dict(start_files: dict, beach: bool = True, age: bool = True, prox: bool = False,
                                 size: bool = False, rho_plastic: bool = False) -> dict:
        var_dict = {}
        for variable in ['lon', 'lat', 'weight']:
            var_dict[variable] = np.load(start_files[variable])
        if beach:
            var_dict['beach'] = np.zeros(len(var_dict['lon']), dtype=np.int32)
        if age:
            var_dict['age'] = np.zeros(len(var_dict['lon']), dtype=np.int32)
        if prox:
            var_dict['prox'] = np.zeros(len(var_dict['lon']), dtype=np.int32)
        if size:
            var_dict['size'] = np.ones(len(var_dict['lon']), dtype=np.float32)*settings.INIT_SIZE
        if rho_plastic:
            var_dict['rho_plastic'] = np.ones(len(var_dict['lon']), dtype=np.float32)*settings.INIT_DENSITY
        return var_dict


