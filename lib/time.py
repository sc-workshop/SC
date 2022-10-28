# Copied from https://gist.github.com/vorono4ka/

UNIT_NAMES = ('msec', 'sec', 'min', 'hour', 'day', 'week')
UNIT_DIVIDERS = (1, 60, 60, 60, 24, 7)
UNIT_FORMATTERS = (lambda unit: round(unit * 1000), round, round, round, round, round)


def time_to_string(value: float):
    assert value >= 0, 'Time cannot be negative.'
    assert len(UNIT_NAMES) == len(UNIT_DIVIDERS) == len(UNIT_FORMATTERS), 'Units count does not match.'

    times = []
    for i in range(len(UNIT_DIVIDERS)):
        divider = UNIT_DIVIDERS[i]
        unit_name = UNIT_NAMES[i]
        unit_formatter = UNIT_FORMATTERS[i]

        unit = value % divider
        value //= divider

        if unit_formatter is not None:
            unit = unit_formatter(unit)

        if unit == 0:
            continue

        times.append(f'{unit} {unit_name}')

    return ' '.join(times[::-1])
