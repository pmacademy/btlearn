from config.app_config import get_config


class CommonConstants:
    CREATE_USER_URL = get_config().AUTH_URL + "/api/v1/user"
