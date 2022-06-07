import base64
import logging
import os
import re

class Route():

    get_routes     = dict()
    post_routes    = dict()
    auth_needed    = dict()
    divert_log_set = set()

    @staticmethod
    def _replace_regex_type(matchobj):

        label, _type = matchobj.groups()

        if _type == 'int':
            expr = r"[1-9][0-9]*|0"
        elif _type == "str":
            expr = r".+"
        elif _type == "date-iso":
            expr = r"[0-9]{4}-[0-1][0-9]-[0-3][0-9]"

        return f"(?P<{label}>{expr})"


    @staticmethod
    def _build_route_pattern(route):
        route_regex = re.sub(r'<(\w+):(int|str|date-iso)>',
                             Route._replace_regex_type, route)
        return re.compile("^{}$".format(route_regex))

    @classmethod
    def get_GET_route(cls, path):

        for pattern in cls.get_routes:

            match = pattern.match(path)

            if match:
                return (match.groupdict(),
                        cls.get_routes[pattern])

        return None

    @classmethod
    def get_POST_route(cls, path):
        if path in cls.post_routes:
            return cls.post_routes[path]
        return None

    @classmethod
    def get(cls, route):

        def decorator_get(func):

            route_pattern = Route._build_route_pattern(route)

            logging.debug("building route '%s' => %s", route_pattern, func)

            cls.get_routes[route_pattern] = func

            return func

        return decorator_get

    @classmethod
    def post(cls, route):
        def decorator_post(func):
            cls.post_routes[route] = func
            return func
        return decorator_post

    @classmethod
    def divert_log(cls):
        def decorator(func):
            cls.divert_log_set.add(func)
            return func
        return decorator

    @classmethod
    def auth(cls, users):
        def decorator(func):
            cls.auth_needed[func] = users
            return func
        return decorator

    @classmethod
    def set_auth_path(cls, auth_dir):
        cls.auth_dir = auth_dir

    @classmethod
    def has_auth(cls, basic_auth, func):

        if func not in cls.auth_needed:
            return True

        if not basic_auth:
            return False

        encoded_auth = basic_auth.split("Basic ")[1]

        user, passwd = (base64
                        .b64decode(bytes(encoded_auth, "ascii"))
                        .decode("utf-8")
                        .split(':'))

        if '/' in user:
            return False

        with open(f"{os.path.join(cls.auth_dir, user)}", "r") as user_auth:
            if user_auth.read() == passwd:
                return True

        return False
