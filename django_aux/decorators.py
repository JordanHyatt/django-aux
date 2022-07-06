
def logtest(logger_method):
    def wrap(test_method):
        def inner(instance):
            logger_method(f'Running {test_method.__name__}')
            test_method(instance)
        return inner
    return wrap


def logtestclass(logger_method):
    def wrap(TestClass):
        logger_method(f'Imported {TestClass.__name__}')
        return TestClass
    return wrap
