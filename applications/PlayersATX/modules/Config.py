import os.path

from applications.s4z4g4.modules.Config import Config, DEPLOYMENT_DIR

PLAYERSATX_CONFIG = os.path.join(DEPLOYMENT_DIR, "playersatx.cfg")


class PlayersATXConfig(Config):

    def __init__(self):
        super(PlayersATXConfig, self).__init__(PLAYERSATX_CONFIG)

playersatxcfg = PlayersATXConfig()
