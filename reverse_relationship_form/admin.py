from functools import partial

from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import ALL_FIELDS

from .forms import reverse_relationship_form_factory


class ReverseFilterSelectMultiple(FilteredSelectMultiple):
    template_name = "admin/widgets/reverse_filter_select_multiple.html"


class ReverseRelationshipAdmin(admin.ModelAdmin):
    related_fields = None
    related_querysets = None
    related_filter_horizontal = None
    related_filter_vertical = None

    def get_form(self, request, obj=None, **kwargs):
        if request.GET.get("_popup") or request.GET.get("_to_field"):
            return super().get_form(request, obj, **kwargs)

        exclude = self.get_exclude(request, obj) or []
        exclude.extend(self.get_readonly_fields(request, obj))
        return reverse_relationship_form_factory(
            self.model,
            fields=self.fields or ALL_FIELDS,
            exclude=exclude,
            widgets=self.get_related_widgets(request, obj),
            formfield_callback=partial(self.formfield_for_dbfield, request=request),
            related_fields=self.related_fields,
            related_querysets=self.get_related_querysets(request, obj),
        )

    def get_related_objects(self):
        return {
            obj.get_accessor_name(): obj for obj in self.model._meta.related_objects
        }

    def get_related_querysets(self, request, obj=None):
        return self.related_querysets

    def get_related_widgets(self, request, obj=None):
        filter_horizontal = self.related_filter_horizontal or []
        filter_vertical = self.related_filter_vertical or []
        filter_fields = [*filter_horizontal, *filter_vertical]
        related_objects = self.get_related_objects()
        widgets = {}
        for field in filter_fields:
            try:
                rel_obj = related_objects[field]
                verbose_name = rel_obj.related_model._meta.verbose_name_plural
            except KeyError:
                # Invalid field
                continue
            widgets[field] = ReverseFilterSelectMultiple(
                verbose_name=verbose_name,
                is_stacked=field in filter_vertical,
            )
        return widgets
