class MalformedObjectError(RuntimeError):
    def __init__(self, error_details=None, prop=None):
        super(MalformedObjectError, self).__init__(error_details, prop)
