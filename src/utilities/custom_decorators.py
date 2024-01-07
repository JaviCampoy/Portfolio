def override_params(new_values):
    def decorator(function_to_decorate):
        def wrapper(self, *args, **kwargs):
            for key, value in new_values.items():
                setattr(self, key, value)

            return function_to_decorate(self, *args, **kwargs)

        setattr(wrapper, '__name__', function_to_decorate.__name__)
        setattr(wrapper, '__doc__', function_to_decorate.__doc__)

        return wrapper

    return decorator
