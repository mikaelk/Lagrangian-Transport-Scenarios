import scenarios.base_scenario as base_scenario
import scenarios.coastal_proximity as prox


class ScenarioFactory:
    @staticmethod
    def create_scenario(scenario_name, server, stokes) -> base_scenario.BaseScenario:
        if scenario_name == "CoastalProximity":
            return prox.CoastalProximity(server=server, stokes=stokes)




