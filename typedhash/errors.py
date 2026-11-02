
class TypedDataError(ValueError):
    def __init__(self, path, message=""):
        super().__init__(f"{path}: {message}" if message else path)
        self.path = path


class TypeNameError(TypedDataError):
    pass


class MissingFieldError(TypedDataError):
    pass


class ExtraFieldError(TypedDataError):
    pass


class ValueTypeError(TypedDataError):
    pass


class RangeError(TypedDataError):
    pass


class LengthError(TypedDataError):
    pass
