import json

def get_version():
    return '2022.12.0-dev'

def f_to_c_conversion(temp_c):
    return (temp_c * 9/5) + 32


def hpa_to_atm_conversion(hpa):
    return hpa * 9.869233e-4


def load_config(level=None, path='config.json'):
    f = open(path)
    try:
        config = json.load(f)
    except ValueError as e:
        raise ValueError(
            f"Configuration file is not fomatted correctly. "
            "Original message follows:\n {e}")

    if level is not None:
        try:
            return config[level]
        except KeyError:
            raise KeyError(
                f"Level {level} is not present in the configuration. "
                "Available levels follow:\n {' '.join(config.keys)}")
    else:
        return config


