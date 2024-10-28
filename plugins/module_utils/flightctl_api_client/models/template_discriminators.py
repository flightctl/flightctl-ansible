from typing import Literal, Set, cast

TemplateDiscriminators = Literal[
    "GitConfigProviderSpec",
    "HttpConfigProviderSpec",
    "InlineConfigProviderSpec",
    "KubernetesSecretProviderSpec",
]

TEMPLATE_DISCRIMINATORS_VALUES: Set[TemplateDiscriminators] = {
    "GitConfigProviderSpec",
    "HttpConfigProviderSpec",
    "InlineConfigProviderSpec",
    "KubernetesSecretProviderSpec",
}


def check_template_discriminators(value: str) -> TemplateDiscriminators:
    if value in TEMPLATE_DISCRIMINATORS_VALUES:
        return cast(TemplateDiscriminators, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {TEMPLATE_DISCRIMINATORS_VALUES!r}"
    )
