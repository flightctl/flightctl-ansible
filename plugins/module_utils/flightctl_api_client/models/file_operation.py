from typing import Literal, Set, cast

FileOperation = Literal["Create", "Reboot", "Remove", "Update"]

FILE_OPERATION_VALUES: Set[FileOperation] = {
    "Create",
    "Reboot",
    "Remove",
    "Update",
}


def check_file_operation(value: str) -> FileOperation:
    if value in FILE_OPERATION_VALUES:
        return cast(FileOperation, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {FILE_OPERATION_VALUES!r}"
    )
