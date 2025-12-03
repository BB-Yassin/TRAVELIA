from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from reservation.models import Reservation
from .models import LoyaltyProgram, PointsTransaction


@receiver(post_save, sender=Reservation)
def update_loyalty_on_reservation(sender, instance, created, **kwargs):
    """
    Signal automatique pour mettre à jour les points de fidélité
    quand une réservation est créée et payée
    """
    try:
        loyalty = LoyaltyProgram.objects.get(user=instance.client)
    except LoyaltyProgram.DoesNotExist:
        # Créer le programme de fidélité si n'existe pas
        loyalty = LoyaltyProgram.objects.create(user=instance.client)
    
    # Récupérer l'hébergement associé à l'offre
    # Note: Vous devez adapter cette logique selon votre relation entre Offre et Hebergement
    try:
        hebergements = instance.offre.hebergements.all()
        hebergement = hebergements.first() if hebergements.exists() else None
    except:
        hebergement = None
    
    if hebergement:
        # Ajouter les points
        points_earned = loyalty.add_points(instance)
        
        # Créer une transaction
        PointsTransaction.objects.create(
            loyalty_program=loyalty,
            transaction_type='earn',
            points_amount=points_earned,
            reservation=instance,
            description=f'Points gagnés de la réservation {instance.id_reservation}'
        )


@receiver(post_delete, sender=Reservation)
def refund_loyalty_on_cancellation(sender, instance, **kwargs):
    """
    Signal automatique pour rembourser les points de fidélité
    quand une réservation est annulée
    """
    try:
        loyalty = LoyaltyProgram.objects.get(user=instance.client)
        
        # Récupérer la transaction correspondante
        transaction = PointsTransaction.objects.filter(
            loyalty_program=loyalty,
            reservation=instance,
            transaction_type='earn'
        ).first()
        
        if transaction:
            # Rembourser les points
            loyalty.points += transaction.points_amount
            loyalty.totalEarnedPoints -= transaction.points_amount
            loyalty.update_tier()
            loyalty.save()
            
            # Créer une transaction de remboursement
            PointsTransaction.objects.create(
                loyalty_program=loyalty,
                transaction_type='earn',
                points_amount=-transaction.points_amount,
                reservation=instance,
                description=f'Points remboursés (annulation réservation {instance.id_reservation})'
            )
    except LoyaltyProgram.DoesNotExist:
        pass
