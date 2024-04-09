from abc import abstractmethod
from typing import Dict, List, Optional, Type, Union


class Labelizer:
    @abstractmethod
    def post_images(self, config: str = 'active'):
        pass
