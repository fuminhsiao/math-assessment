from django.contrib import admin
from .models import Answer, Choice, Question, QuestionSet, QuestionSetItem, Submission

admin.site.site_header = "Math Assessment Administration"
admin.site.site_title = "Math Assessment Admin"
admin.site.index_title = "Question Bank and Submissions"


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "short_prompt", "question_type", "order", "is_active")
    list_filter = ("question_type", "is_active")
    search_fields = ("prompt",)
    inlines = [ChoiceInline]

    @admin.display(description="Question")
    def short_prompt(self, obj):
        return obj.prompt[:70]


class QuestionSetItemInline(admin.TabularInline):
    model = QuestionSetItem
    extra = 0


@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ("title", "public_id", "created_at")
    inlines = [QuestionSetItemInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ("question", "answer_text", "is_correct")
    can_delete = False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student_name", "question_set", "submitted_at")
    inlines = [AnswerInline]


admin.site.register(Choice)
