from typing import Literal, Set, cast

FileSpecContentEncoding = Literal["base64", "plain"]

FILE_SPEC_CONTENT_ENCODING_VALUES: Set[FileSpecContentEncoding] = {
    "base64",
    "plain",
}


def check_file_spec_content_encoding(value: str) -> FileSpecContentEncoding:
    if value in FILE_SPEC_CONTENT_ENCODING_VALUES:
        return cast(FileSpecContentEncoding, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {FILE_SPEC_CONTENT_ENCODING_VALUES!r}"
    )
