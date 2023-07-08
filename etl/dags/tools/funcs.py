_true_values = {"1", "true", "t", "yes", "y"}


def str_to_bool(v: str | None) -> bool:
    """
    Converts string to bool
    :param v:
    :return:
    """
    if v is None:
        return False
    return v.lower().strip() in _true_values


def str_to_int(v: str) -> int:
    return int(v.lower().strip())
