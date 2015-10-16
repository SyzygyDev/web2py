import os.path

from applications.s4z4g4.modules.Config import Config, DEPLOYMENT_DIR

FITNESSSITE_CONFIG = os.path.join(DEPLOYMENT_DIR, "fitness.cfg")


class FitnessSiteConfig(Config):

    def __init__(self):
        super(FitnessSiteConfig, self).__init__(FITNESSSITE_CONFIG)

fitnessSitecfg = FitnessSiteConfig()
