from parcels import FieldSet, ParticleSet
import numpy as np
import settings as settings
import scenarios.base_scenario as base_scenario
import factories.fieldset_factory as fieldset_factory
import utils as utils
from datetime import datetime, timedelta


class CoastalProximity(base_scenario.BaseScenario):
    """Coastal proximity scenario"""
    def __init__(self, server, stokes):
        """Constructor for coastal_proximity"""
        super().__init__(server, stokes)
        self.prefix = "Prox"
        self.input_dir = utils._get_input_directory(server=self.server)

    var_list = ['lon', 'lat', 'beach', 'age', 'weights', 'prox']

    def create_fieldset(self) -> FieldSet:
        fieldset = fieldset_factory.FieldSetFactory().create_fieldset(server=self.server, stokes=self.stokes,
                                                                      border_current=True, diffusion=True,
                                                                      landID=True, distance=True, vicinity=True)
        return fieldset

    def _get_pset(self, fieldset: FieldSet, particle_type: utils.BaseParticle, var_dict: dict,
                   start_time: datetime, repeat_dt: timedelta):
        """

        :return:
        """
        pset = ParticleSet(fieldset=fieldset, pclass=particle_type,
                           lon=var_dict['lon'], lat=var_dict['lat'], beach=var_dict['beach'],
                           age=var_dict['age'], prox=var_dict['prox'], weights=var_dict['weights'],
                           time=start_time, repeatdt=repeat_dt)
        return pset

    def _get_pclass(self):
        particle_type = utils.BaseParticle
        utils._add_var_particle(particle_type, 'prox')
        utils._add_var_particle(particle_type, 'distance', dtype=np.float32, set_initial=False)

    def _file_names(self, new: bool = False):
        odirec = self.input_dir + "coastal_v_" + str(settings.VICINITY) + "_e_" + str(settings.ENSEMBLE) + "/"
        if new==True:
            return odirec + self.prefix + "_v=" + str(settings.VICINITY) + "_y=" + str(settings.START_YEAR) + "_I=" + \
                    str(settings.INPUT) + "_r=" + str(settings.RESTART) + "_run=" + str(settings.RESTART) + ".nc"
        else:
            return odirec + self.prefix + "_v=" + str(settings.VICINITY) + "_y=" + str(settings.START_YEAR) + "_I=" + \
                    str(settings.INPUT) + "_r=" + str(settings.RESTART - 1) + "_run=" + str(settings.RESTART) + ".nc"

    # def _get_var_dict(self):
    #     if settings.RESTART==0:
    #         return self._get_var_dict()
    #     else:
    #         return self._get_restart_variables(rfile=self.self._file_names(new=False),var_list=self.var_list)

    def _beaching_kernel(particle, fieldset, time):
        if particle.beach == 0:
            dist = fieldset.distance2shore[time, particle.depth, particle.lat, particle.lon]
            # If a particle is within 10 km of the shore
            if dist < 10:
                particle.proximity += particle.dt
            else:
                particle.proximity = 0.
            if particle.proximity > 86400 * fieldset.vic:
                particle.beach = 1
        # Update the age of the particle
        particle.age += particle.dt


    def _get_particle_behavior(self, pset: ParticleSet):
        base_behavior = pset.Kernel(utils._initial_input) + pset.Kernel(utils._floating_advection_rk4) + \
                        pset.Kernel(utils._floating_2d_brownian_motion)
        total_behavior = base_behavior + pset.Kernel(utils._anti_beach_nudging) + pset.Kernel(self._beaching_kernel)
        return total_behavior
