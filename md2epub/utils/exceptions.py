from functools import partial, wraps

import click

from md2epub.utils.logging import get_logger


def catch_exception(func=None, *, handle, message=None):
    if not func:
        return partial(catch_exception, handle=handle)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except handle as e:
            message = f"Error occurs in '{func.__name__}' command!"

            get_logger().exception(message)
            raise click.ClickException(e)

    return wrapper
