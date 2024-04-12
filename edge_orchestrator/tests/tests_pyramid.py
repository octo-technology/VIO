import logging
import re
from pathlib import Path
from typing import Tuple

import click

PARENT_DIR = Path(__file__).parent


@click.command("measure-tests-pyramid-and-create-gitlab-badges")
@click.option("--badges-generation/--no-badges-generation", default=False)
def measure_tests_pyramid_and_create_gitlab_badges(badges_generation: bool):
    (
        number_of_func_tests,
        number_of_int_tests,
        number_of_unit_tests,
    ) = compute_number_of_each_test_type()
    total_number_of_tests = number_of_unit_tests + number_of_int_tests + number_of_func_tests

    percentage_of_unit_tests = percentage(number_of_unit_tests, total_number_of_tests)
    percentage_of_int_tests = percentage(number_of_int_tests, total_number_of_tests)
    percentage_of_func_tests = percentage(number_of_func_tests, total_number_of_tests)

    print(
        f"""\n
        \033[96m      /\\
             /|_\\         [*] functional tests:   {number_of_func_tests}/{total_number_of_tests} --> {percentage_of_func_tests:.2f} %
        \033[94m    /__|_\\
           /__|__|\\       [*] integration tests: {number_of_int_tests}/{total_number_of_tests} --> {percentage_of_int_tests:.2f} %
        \033[92m  /_|__|__|\\
         /|__|___|__\\     [*] unit tests:        {number_of_unit_tests}/{total_number_of_tests} --> {percentage_of_unit_tests:.2f} %
        /__|___|___|_\\\033[0m
\n"""  # noqa
    )

    check_if_pyramid_is_ok(number_of_unit_tests, number_of_int_tests, number_of_func_tests)

    if badges_generation:
        import anybadge

        badges_dir = PARENT_DIR.parent / "badges"
        badges_dir.mkdir(parents=True, exist_ok=True)
        unit_test_file = (badges_dir / "badge_unit_tests.svg").as_posix()
        int_test_file = (badges_dir / "badge_int_tests.svg").as_posix()
        func_test_file = (badges_dir / "badge_func_tests.svg").as_posix()

        func_color, int_color, unit_color = get_color_according_to_percentage(
            percentage_of_func_tests, percentage_of_int_tests, percentage_of_unit_tests
        )

        anybadge.Badge(
            label="unit-tests-ratio",
            value=f"{percentage_of_unit_tests:.2f} %",
            default_color=unit_color,
        ).write_badge(unit_test_file, overwrite=True)
        anybadge.Badge(
            label="integration-tests-ratio",
            value=f"{percentage_of_int_tests:.2f} %",
            default_color=int_color,
        ).write_badge(int_test_file, overwrite=True)
        anybadge.Badge(
            label="functional-tests-ratio",
            value=f"{percentage_of_func_tests:.2f} %",
            default_color=func_color,
        ).write_badge(func_test_file, overwrite=True)


def compute_number_of_each_test_type(
    path_to_unit_tests: Path = PARENT_DIR / "unit_tests",
    path_to_integration_tests: Path = PARENT_DIR / "integration_tests",
    path_to_functional_tests: Path = PARENT_DIR / "functional_tests",
    test_function_pattern: re.Pattern = re.compile("def test_"),
    test_scenario_pattern: re.Pattern = re.compile("Scenario:"),
) -> Tuple[int, int, int]:
    number_of_unit_tests = count_tests(path_to_unit_tests, test_function_pattern)
    number_of_int_tests = count_tests(path_to_integration_tests, test_function_pattern)
    number_of_func_tests = count_tests(path_to_functional_tests, test_scenario_pattern, "feature")
    return number_of_func_tests, number_of_int_tests, number_of_unit_tests


def count_tests(path: Path, test_function_pattern: re.Pattern, file_extension="py") -> int:
    counter = 0
    for filepath in path.glob(f"**/*.{file_extension}"):
        with filepath.open("r") as f:
            one_line = f.readline()
            while one_line:
                if re.search(test_function_pattern, one_line):
                    counter += 1
                one_line = f.readline()
    return counter


def percentage(number_of_unit_tests: int, total_number_of_tests: int) -> float:
    return number_of_unit_tests / total_number_of_tests * 100


def get_color_according_to_percentage(percentage_of_func_tests, percentage_of_int_tests, percentage_of_unit_tests):
    func_color, int_color, unit_color = "green", "green", "green"
    if percentage_of_func_tests <= 1 or percentage_of_func_tests >= 20:
        func_color = "brightred"
    if percentage_of_int_tests <= 10 or percentage_of_int_tests >= 40:
        int_color = "brightred"
    if percentage_of_unit_tests <= 40 or percentage_of_func_tests >= 90:
        unit_color = "brightred"
    return func_color, int_color, unit_color


def check_if_pyramid_is_ok(number_of_unit_tests: int, number_of_int_tests: int, number_of_func_tests: int):
    if (
        number_of_func_tests > number_of_int_tests
        or number_of_func_tests > number_of_unit_tests
        or number_of_int_tests > number_of_unit_tests
    ):
        logging.warning("Tests pyramid is unbalanced")


if __name__ == "__main__":
    measure_tests_pyramid_and_create_gitlab_badges()
