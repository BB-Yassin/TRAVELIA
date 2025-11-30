# feedback/admin.py
from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_submitter', 'offer', 'note', 'date_soumission')
    search_fields = ('user__first_name', 'user__last_name', 'offer__title', 'description')
    list_filter = ('note', 'date_soumission')

    def get_submitter(self, obj):
        return obj.submitter_name()
    get_submitter.short_description = 'Utilisateur'
