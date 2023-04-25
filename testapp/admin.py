from django.contrib import admin

from .forms.complete import CompleteForm
from .models import Company, Team, Member


# @admin.register(DummyModel)
class DummyAdmin(admin.ModelAdmin):
    form = CompleteForm
    change_form_template = 'admin/formset/change_form.html'


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    class TeamInline(admin.TabularInline):
        extra = 1
        model = Team
    inlines = [TeamInline]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    class MemberInline(admin.TabularInline):
        extra = 1
        model = Member
    inlines = [MemberInline]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass
