from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, Wallet


@receiver(post_save, sender=Profile)
def ensure_wallet_for_profile(sender, instance: Profile, created: bool, **_: object) -> None:
    """Create a wallet for every new profile automatically."""

    if created:
        Wallet.objects.get_or_create(profile=instance)
