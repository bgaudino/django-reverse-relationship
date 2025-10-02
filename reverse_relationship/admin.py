from functools import partial
from typing import Mapping, Optional, Sequence

from django.db.models import ForeignKey, ManyToOneRel, ManyToManyRel, IntegerField
from django.contrib import admin
from django.contrib.admin.widgets import (
    FilteredSelectMultiple,
    RelatedFieldWidgetWrapper,
)
from django.core.exceptions import FieldError
from django.forms.models import ALL_FIELDS
from django.forms.widgets import SelectMultiple

from .forms import reverse_relationship_form_factory


class ReverseRelationshipAdmin(admin.ModelAdmin):
    related_fields: Optional[Sequence] = None
    related_querysets: Optional[Mapping] = None
    related_labels: Optional[Mapping] = None
    related_filter_horizontal: Optional[Sequence] = None
    related_filter_vertical: Optional[Sequence] = None

    def get_form(self, request, obj=None, change=False, **kwargs):
        if request.GET.get("_popup") or request.GET.get("_to_field"):
            return super().get_form(request, obj, change, **kwargs)

        related_fields = self.get_related_fields(request, obj)
        related_querysets = self.get_related_querysets(request, obj)
        related_labels = self.get_related_labels(request, obj)
        exclude = self.get_exclude(request, obj) or ()
        readonly_fields = self.get_readonly_fields(request, obj) or ()

        return reverse_relationship_form_factory(
            self.model,
            fields=self.fields or ALL_FIELDS,
            exclude=(*exclude, *readonly_fields),
            widgets=self.get_related_widgets(request, obj),
            formfield_callback=partial(self.formfield_for_dbfield, request=request),
            related_fields=related_fields,
            related_querysets=related_querysets,
            labels=related_labels,
        )

    def get_related_objects(self):
        return {
            obj.get_accessor_name(): obj for obj in self.model._meta.related_objects
        }

    def get_related_fields(self, request, obj=None):
        """Hook for specifying related fields"""
        return self.related_fields

    def get_related_querysets(self, request, obj=None):
        """Hook for specifying customizing querysets for related fields"""
        return self.related_querysets

    def get_related_labels(self, request, obj=None):
        """Hook for specifying labels for related fields"""
        return self.related_labels

    def get_related_widgets(self, request, obj=None):
        filter_horizontal = self.related_filter_horizontal or []
        filter_vertical = self.related_filter_vertical or []
        filter_fields = [*filter_horizontal, *filter_vertical]
        related_objects = self.get_related_objects()
        widgets = {}
        for field in self.related_fields or []:
            try:
                rel_obj = related_objects[field]
            except KeyError:
                raise FieldError(f"Invalid reverse related field: {field}")
            if field in filter_fields:
                widget = FilteredSelectMultiple(
                    verbose_name=rel_obj.related_model._meta.verbose_name_plural,
                    is_stacked=field in filter_vertical,
                )
            else:
                widget = SelectMultiple()
            if isinstance(rel_obj, ManyToManyRel):
                rel = ManyToManyRel(
                    field=rel_obj.field,
                    to=rel_obj.related_model,
                    through=rel_obj.through,
                )
            elif isinstance(rel_obj, ManyToOneRel):
                for f in rel_obj.related_model._meta.fields:
                    if isinstance(f, ForeignKey) and f.related_model is rel_obj.model:
                        rel = ManyToOneRel(
                            field=IntegerField(),
                            to=rel_obj.related_model,
                            field_name="id",
                        )
                        break
                else:
                    # Invalid field
                    continue
            else:
                # Invalid field
                continue
            widgets[field] = RelatedFieldWidgetWrapper(
                widget=widget,
                rel=rel,
                admin_site=admin.site,
            )
        return widgets
