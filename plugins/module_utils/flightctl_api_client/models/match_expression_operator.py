from typing import Literal, Set, cast

MatchExpressionOperator = Literal["DoesNotExist", "Exists", "In", "NotIn"]

MATCH_EXPRESSION_OPERATOR_VALUES: Set[MatchExpressionOperator] = {
    "DoesNotExist",
    "Exists",
    "In",
    "NotIn",
}


def check_match_expression_operator(value: str) -> MatchExpressionOperator:
    if value in MATCH_EXPRESSION_OPERATOR_VALUES:
        return cast(MatchExpressionOperator, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {MATCH_EXPRESSION_OPERATOR_VALUES!r}"
    )
