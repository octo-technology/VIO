from abc import abstractmethod


class Labelizer:
    @abstractmethod
    def post_images(self, config: str):
        pass
