from typing import Literal, Set, cast

RepoSpecType = Literal["git", "http"]

REPO_SPEC_TYPE_VALUES: Set[RepoSpecType] = {
    "git",
    "http",
}


def check_repo_spec_type(value: str) -> RepoSpecType:
    if value in REPO_SPEC_TYPE_VALUES:
        return cast(RepoSpecType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {REPO_SPEC_TYPE_VALUES!r}"
    )
