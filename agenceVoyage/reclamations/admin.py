from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Reclamation, ReclamationComment

@admin.register(Reclamation)
class ReclamationAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'get_submitter', 'type_de_reclamation', 'priorite', 'status', 'date_creation', 'sla_deadline', 'breach_flag', 'is_resolved')
    list_filter = ('priorite', 'status', 'date_creation', 'type_de_reclamation', 'breach_flag')
    search_fields = ('client__first_name', 'client__last_name', 'type_de_reclamation', 'description', 'reservation__id')
    readonly_fields = ('date_creation', 'date_resolution', 'sla_deadline', 'breach_flag')
    list_editable = ('status', 'priorite')
    
    fieldsets = (
        ('Informations Client & Réservation', {
            'fields': ('client', 'reservation')
        }),
        ('Détails de la Réclamation', {
            'fields': ('type_de_reclamation', 'description', 'priorite', 'status')
        }),
        ('SLA & Dates', {
            'fields': ('date_creation', 'date_resolution', 'sla_deadline', 'breach_flag'),
            'classes': ('collapse',)
        }),
    )

    def get_submitter(self, obj):
        return obj.submitter_name()
    get_submitter.short_description = 'Client'
    get_submitter.admin_order_field = 'client__first_name'

    def is_resolved(self, obj):
        return obj.status in ('resolu', 'ferme')
    is_resolved.boolean = True
    is_resolved.short_description = 'Résolu'


@admin.register(ReclamationComment)
class ReclamationCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'reclamation_link', 'get_submitter', 'short_description', 'date_added')
    search_fields = ('description', 'user__first_name', 'user__last_name', 'reclamation__type_de_reclamation')
    list_filter = ('date_added',)
    autocomplete_fields = ['reclamation', 'user']

    def get_submitter(self, obj):
        return obj.submitter_name()
    get_submitter.short_description = 'Utilisateur'

    def short_description(self, obj):
        # show a truncated preview of the comment in list view
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
    short_description.short_description = 'Commentaire'

    def reclamation_link(self, obj):
        return obj.reclamation
    reclamation_link.short_description = 'Réclamation'
