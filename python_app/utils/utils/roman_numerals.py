# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Roman numeral conversion utilities - Migration from OCaml Mutil module.
"""


def roman_of_arabian(n: int) -> str:
    def build(one: str, five: str, ten: str, digit: int) -> str:
        if digit == 0:
            return ""
        elif digit == 1:
            return one
        elif digit == 2:
            return one + one
        elif digit == 3:
            return one + one + one
        elif digit == 4:
            return one + five
        elif digit == 5:
            return five
        elif digit == 6:
            return five + one
        elif digit == 7:
            return five + one + one
        elif digit == 8:
            return five + one + one + one
        else:
            return one + ten

    thousands = build("M", "M", "M", (n // 1000) % 10)
    hundreds = build("C", "D", "M", (n // 100) % 10)
    tens = build("X", "L", "C", (n // 10) % 10)
    units = build("I", "V", "X", n % 10)
    return thousands + hundreds + tens + units


def arabian_of_roman(s: str) -> int:
    def decode_digit(one: str, five: str, ten: str, r: int, i: int) -> tuple[int, int]:
        def loop(cnt: int, idx: int) -> tuple[int, int]:
            if idx >= len(s):
                return (10 * r + cnt, idx)
            elif s[idx] == one:
                return loop(cnt + 1, idx + 1)
            elif s[idx] == five:
                if cnt == 0:
                    return loop(5, idx + 1)
                else:
                    return (10 * r + 5 - cnt, idx + 1)
            elif s[idx] == ten:
                return (10 * r + 10 - cnt, idx + 1)
            else:
                return (10 * r + cnt, idx)

        return loop(0, i)

    if not s:
        raise ValueError("Empty Roman numeral string")

    r, i = decode_digit('M', 'M', 'M', 0, 0)
    r, i = decode_digit('C', 'D', 'M', r, i)
    r, i = decode_digit('X', 'L', 'C', r, i)
    r, i = decode_digit('I', 'V', 'X', r, i)
    if i != len(s):
        raise ValueError(f"Invalid Roman numeral: {s}")
    return r


