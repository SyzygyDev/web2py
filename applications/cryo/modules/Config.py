import os.path

from applications.s4z4g4.modules.Config import Config, DEPLOYMENT_DIR

CRYO_CONFIG = os.path.join(DEPLOYMENT_DIR, "cryo.cfg")


class CryoConfig(Config):

    def __init__(self):
        super(CryoConfig, self).__init__(CRYO_CONFIG)

croycfg = CryoConfig()
