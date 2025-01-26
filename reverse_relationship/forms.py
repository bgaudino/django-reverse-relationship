from django.core.exceptions import FieldError
from django.db.models import ManyToOneRel
from django.forms import ModelForm, ModelMultipleChoiceField, modelform_factory


def reverse_relationship_form_factory(
    model,
    form=ModelForm,
    related_fields=None,
    related_querysets=None,
    related_labels=None,
    **kwargs,
):
    if related_fields is None:
        related_fields = []
    if related_querysets is None:
        related_querysets = {}
    labels = kwargs.get("labels") or {}
    if related_labels:
        labels.update(related_labels)
    widgets = kwargs.get("widgets") or {}

    form_class = modelform_factory(model, form, **kwargs)

    related_objects = {}
    for obj in model._meta.related_objects:
        field_name = obj.get_accessor_name()
        if field_name not in related_fields:
            continue
        if isinstance(obj, ManyToOneRel) and not obj.field.null:
            raise FieldError(
                f"Cannot use non nullable reverse relationship ({field_name}) in ReverseReverseRelationshipForm"
            )
        related_objects[field_name] = obj

    if invalid_fields := set(related_fields).difference(set(related_objects)):
        raise FieldError(
            f"Unknown field(s) for {model._meta.verbose_name}: {invalid_fields}"
        )

    form_class_attrs = {}
    for field_name, obj in related_objects.items():
        queryset = related_querysets.get(field_name, obj.related_model.objects.all())
        label = labels.get(field_name, obj.related_model._meta.verbose_name_plural)
        widget = widgets.get(field_name)
        form_class_attrs[field_name] = ModelMultipleChoiceField(
            queryset=queryset,
            label=label.capitalize(),
            required=False,
            widget=widget,
        )

    def __init__(self, *args, **kwargs):
        super(form, self).__init__(*args, **kwargs)
        if self.instance.pk:
            for field in related_objects:
                self.fields[field].initial = getattr(self.instance, field).all()

    def _save_m2m(self):
        super(form, self)._save_m2m()
        for field in related_objects:
            getattr(self.instance, field).set(self.cleaned_data[field])

    form_class_attrs["__init__"] = __init__
    form_class_attrs["_save_m2m"] = _save_m2m

    class_name = model.__name__ + "ReverseRelationshipForm"

    return type(form_class)(class_name, (form_class,), form_class_attrs)
