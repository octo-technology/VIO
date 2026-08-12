class ConfigNotFoundError(Exception):
    pass


class InvalidConfigNameError(Exception):
    pass


class ModelNotInConfigError(Exception):
    """Raised when an action targets a model absent from the active station config."""

    pass
