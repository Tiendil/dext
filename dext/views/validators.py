# coding: utf-8

import functools


def validator(code=None, message=None, response_type=None):

    @functools.wraps(validator)
    def validator_decorator(checker):

        @functools.wraps(checker)
        def validator_wrapper(code=code, message=message, response_type=response_type):

            @functools.wraps(validator_wrapper)
            def view_decorator(view):

                @functools.wraps(view)
                def view_wrapper(resource, **kwargs):

                    if not checker(resource, **kwargs):
                        return resource.auto_error(code=code, message=message,  response_type=response_type)

                    return view(resource, **kwargs)

                return view_wrapper

            return view_decorator

        return validator_wrapper

    return validator_decorator


def validate_argument(argument_name, checker, code_prefix=None, message=None, response_type=None):

    @functools.wraps(validate_argument)
    def view_decorator(view):

        @functools.wraps(view)
        def view_wrapper(resource, **kwargs):

            if argument_name not in kwargs:
                return view(resource, **kwargs)

            try:
                value = checker(kwargs[argument_name])
            except:
                return resource.auto_error(code='%s.%s.wrong_format' % (code_prefix, argument_name), message=message, response_type=response_type)

            if value is None:
                return resource.auto_error(code='%s.%s.not_found' % (code_prefix, argument_name), message=message, response_type=response_type, status_code=404)

            kwargs[argument_name] = value

            return view(resource, **kwargs)

        return view_wrapper

    return view_decorator
