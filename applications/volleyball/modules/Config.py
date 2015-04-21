import os.path

from applications.s4z4g4.modules.Config import Config, DEPLOYMENT_DIR

VOLLEYBALL_CONFIG = os.path.join(DEPLOYMENT_DIR, "volleyball.cfg")


class VolleyBallConfig(Config):

    def __init__(self):
        super(VolleyBallConfig, self).__init__(VOLLEYBALL_CONFIG)

volleyballcfg = VolleyBallConfig()
