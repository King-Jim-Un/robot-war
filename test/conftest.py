# Globals:
G_CALLED_FROM_TEST = False


def pytest_configure(config):
    global G_CALLED_FROM_TEST
    G_CALLED_FROM_TEST = True
