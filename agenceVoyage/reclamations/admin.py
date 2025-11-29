from django.contrib import admin
from .models import Reclamation, ReclamationComment

@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_submitter', 'type_de_reclamation', 'priorite', 'status', 'date_creation', 'date_resolution')
    list_filter = ('priorite', 'status', 'date_creation')
    search_fields = ('client__first_name', 'client__last_name', 'type_de_reclamation', 'description')

    def get_submitter(self, obj):
        return obj.submitter_name()
    get_submitter.short_description = 'Client'


@admin.register(ReclamationComment)
class ReclamationCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'reclamation', 'get_submitter', 'short_description', 'date_added')
    search_fields = ('description', 'user__first_name', 'user__last_name', 'reclamation__type_de_reclamation')

    def get_submitter(self, obj):
        return obj.submitter_name()
    get_submitter.short_description = 'Utilisateur'

    def short_description(self, obj):
        # show a truncated preview of the comment in list view
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
    short_description.short_description = 'Commentaire'
