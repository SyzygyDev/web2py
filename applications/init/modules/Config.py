import os.path

from applications.s4z4g4.modules.Config import Config, DEPLOYMENT_DIR

MAINSITE_CONFIG = os.path.join(DEPLOYMENT_DIR, "main.cfg")


class MainSiteConfig(Config):

    def __init__(self):
        super(MainSiteConfig, self).__init__(MAINSITE_CONFIG)

mainSitecfg = MainSiteConfig()
