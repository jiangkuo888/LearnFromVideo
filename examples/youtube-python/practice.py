"""Original small exercises for concepts observed in the video; standard library only."""

import json
from pathlib import Path


def squares(values):
    result = []
    for value in values:
        result.append(value * value)
    return result


def main():
    checks = {}
    checks["function_loop_indentation"] = squares([1, 2, 3]) == [1, 4, 9]
    checks["lambda_map"] = list(map(lambda n: n + 1, [1, 2, 3])) == [2, 3, 4]
    containers = {"tuple": (1, 2), "list": [1, 2], "dictionary": {"one": 1}}
    checks["container_literals"] = containers["dictionary"]["one"] == containers["tuple"][0]
    binding = 1
    binding = "one"
    checks["dynamic_binding"] = isinstance(binding, str)
    try:
        _ = "1" + 1
    except TypeError:
        checks["no_implicit_string_integer_addition"] = True
    else:
        checks["no_implicit_string_integer_addition"] = False
    output = {"passed": all(checks.values()), "checks": checks}
    Path(__file__).with_name("practice-result.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output))
    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
