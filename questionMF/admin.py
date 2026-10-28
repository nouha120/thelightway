from django.contrib import admin

from questionMF.models import Question, UserQuizSubmission


admin.site.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text',)
    search_fields = ('question_text',)
admin.site.register(UserQuizSubmission)
class UserQuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('username', 'total_score', 'submitted_at')
    search_fields = ('username',)
    list_filter = ('submitted_at',)