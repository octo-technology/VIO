from pathlib import Path

from hub_labelizer.ports.labelizer import Labelizer


class Config:
    ROOT_PATH = Path(__file__).parents[2]

    labelizer: Labelizer = None

    def get_labelizer(self):
        return self.labelizer
