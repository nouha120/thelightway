import csv
from django.http import HttpResponse

from users.models import User
from .models import MedicalCategory, MedicalQuestion, MedicalQuestionAnswer, MedicalRecord
from django.contrib import admin
# Register your models here.
admin.site.register(MedicalRecord)

class MedicalQuestionInline(admin.TabularInline):
    model = MedicalQuestion
    extra = 1  # عدد الأسطر الفارغة لإضافة أسئلة جديدة مباشرة

class MedicalCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [MedicalQuestionInline]  # عرض الأسئلة المرتبطة بالفئة مباشرة داخلها
    search_fields = ['name']

class MedicalQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category')
    list_filter = ('category',)
    search_fields = ['text', 'category__name']

admin.site.register(MedicalCategory, MedicalCategoryAdmin)
admin.site.register(MedicalQuestion, MedicalQuestionAdmin)



@admin.register(MedicalQuestionAnswer)
class MedicalQuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('get_firebase_uid', 'get_username', 'category', 'short_question', 'short_answer', 'created_at')
    list_filter = ('user__firebase_uid', 'category', 'created_at')  # ✅ فلترة حسب firebase_uid
    search_fields = ('user__firebase_uid', 'user__username', 'category', 'question', 'answer')  # ✅ بحث حسب UID و Username
    ordering = ['user__firebase_uid', 'created_at']  # ✅ ترتيب حسب firebase_uid أولا ثم زمن الإجابة
    actions = ['export_as_csv']
    def get_firebase_uid(self, obj):
        return obj.user.firebase_uid
    get_firebase_uid.short_description = 'Firebase UID'

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def short_question(self, obj):
        return (obj.question[:50] + '...') if len(obj.question) > 50 else obj.question

    def short_answer(self, obj):
        return (obj.answer[:50] + '...') if obj.answer and len(obj.answer) > 50 else obj.answer
    
    
    def export_as_csv(self, request, queryset):
        """ تصدير الإجابات المختارة إلى ملف CSV """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="medical_question_answers.csv"'

        writer = csv.writer(response)
        writer.writerow(['Firebase UID', 'Username', 'Category', 'Question', 'Answer', 'Created At'])

        for obj in queryset:
            writer.writerow([
                obj.user.firebase_uid,
                obj.user.username,
                obj.category,
                obj.question,
                obj.answer,
                obj.created_at
            ])

        return response
    export_as_csv.short_description = "Export Selected to CSV"