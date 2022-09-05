from django.db import models

from company.models import Company
from oauth2_provider.models import AbstractGrant, AbstractApplication, AbstractAccessToken, AbstractRefreshToken, AbstractIDToken
# Create your models here.

class CustomAbstractGrant(AbstractGrant):
    user = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s"
    )

class CustomGrant(CustomAbstractGrant):
    class Meta(CustomAbstractGrant.Meta):
        swappable = "OAUTH2_PROVIDER_GRANT_MODEL"


class CustomAbstractAccessToken(AbstractAccessToken):
    user = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s",
    )

class CustomAccessToken(CustomAbstractAccessToken):
    class Meta(CustomAbstractAccessToken.Meta):
        swappable = "OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL"


class CustomAbstractRefreshToken(AbstractRefreshToken):
    user = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s"
    )
    class Meta:
        abstract = True
        unique_together = (
            "token",
            "revoked",
        )



class CustomRefreshToken(CustomAbstractRefreshToken):
    class Meta(AbstractRefreshToken.Meta):
        swappable = "OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL"

class CustomAbstractIDToken(AbstractIDToken):
    user = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s",
    )

class CustomIDToken(CustomAbstractIDToken):
    class Meta(CustomAbstractIDToken.Meta):
        swappable = "OAUTH2_PROVIDER_ID_TOKEN_MODEL"


class MyApplication(AbstractApplication):
    pass