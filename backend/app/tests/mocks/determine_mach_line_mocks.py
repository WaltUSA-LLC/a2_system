def make_valid_mach_line_cases() -> list[tuple[int, int]]:
    return [
        (1, 1),
        (2, 2),
        (21, 1),
        (22, 2),
        (41, 1),
        (42, 2),
        (43, 3),
        (44, 4),
        (63, 3),
        (64, 4),
        (83, 3),
        (84, 4),
        (85, 5),
        (86, 6),
        (105, 5),
        (106, 6),
        (125, 5),
        (126, 6),
    ]


def make_non_positive_mach_ids() -> list[int]:
    return [0, -1, -2, -42, -126]


def make_out_of_range_mach_ids() -> list[int]:
    return [127, 128, 999]
