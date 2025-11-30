from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'get_submitter', 'offer', 'note_service', 'note_hebergement','note_valeur', 'date_soumission', 'has_attachment')
    search_fields = ('user__first_name', 'user__last_name', 'offer__titre', 'description')
    list_filter = ('user__first_name', 'user__last_name', 'date_soumission', 'offer')
    readonly_fields = ('date_soumission',)
    autocomplete_fields = ['user', 'offer']
    fieldsets = (
        ('Informations Générales', {
            'fields': ('user', 'offer', 'date_soumission')
        }),
        ('Notation Détaillée', {
            'fields': ('note_service', 'note_hebergement', 'note_valeur')
        }),
        ('Détails du Feedback', {
            'fields': ('description', 'attachement')
        }),
    )

    def get_submitter(self, obj):
        return obj.submitter_name()
    get_submitter.short_description = 'Utilisateur'
    get_submitter.admin_order_field = 'user__first_name'

    def has_attachment(self, obj):
        return bool(obj.attachement)
    has_attachment.boolean = True
    has_attachment.short_description = 'Pièce jointe'
