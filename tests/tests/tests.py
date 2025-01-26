from django.core.exceptions import FieldError
from django.contrib.admin.widgets import (
    FilteredSelectMultiple,
    RelatedFieldWidgetWrapper,
)
from django.contrib.auth import get_user_model
from django.forms.models import ALL_FIELDS
from django.forms.widgets import SelectMultiple
from django.test import TestCase
from django.urls import reverse

from . import models
from .admin import ToppingAdmin
from reverse_relationship.forms import reverse_relationship_form_factory


class BaseTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For django < 4.0
        if not hasattr(self, "assertQuerySetEqual"):
            self.assertQuerySetEqual = self.assertQuerysetEqual

    def setUp(self):
        self.veggie = models.Pizza.objects.create(name="Veggie")
        self.mediterranean = models.Pizza.objects.create(name="Mediterranean")
        self.mushrooms = models.Topping.objects.create(name="Mushrooms")


class ReverseRelationshipFormTestCase(BaseTestCase):
    def get_form_class(self, **kwargs):
        related_fields = kwargs.pop("related_fields", ["pizza_set"])
        return reverse_relationship_form_factory(
            models.Topping,
            fields=kwargs.get("fields", ALL_FIELDS),
            related_fields=related_fields,
            **kwargs,
        )

    def test_form_has_related_fields(self):
        form = self.get_form_class()()
        self.assertIn("pizza_set", form.fields)

    def test_form_saves_related_fields(self):
        form = self.get_form_class()(
            data={"name": "olives", "pizza_set": [self.veggie.pk]}
        )
        topping = form.save()
        self.assertIsNotNone(topping.pk)
        self.assertEqual(topping.name, "olives")
        self.assertQuerySetEqual(topping.pizza_set.all(), [self.veggie])

    def test_related_queryset(self):
        form = self.get_form_class()()
        self.assertQuerySetEqual(
            form.fields["pizza_set"].queryset.order_by("pk"),
            [self.veggie, self.mediterranean],
        )
        querysets = {"pizza_set": models.Pizza.objects.filter(name__istartswith="v")}
        form = self.get_form_class(related_querysets=querysets)()
        self.assertQuerySetEqual(form.fields["pizza_set"].queryset, [self.veggie])

    def test_initial_value(self):
        mushrooms = models.Topping.objects.create(name="mushrooms")
        self.veggie.toppings.add(mushrooms)
        form = self.get_form_class()(instance=mushrooms)
        self.assertQuerySetEqual(form.fields["pizza_set"].initial, [self.veggie])

    def test_invalid_field(self):
        with self.assertRaises(FieldError):
            self.get_form_class(related_fields=["foo"])()

    def test_non_null_fk_raises_exception(self):
        with self.assertRaises(FieldError):
            self.get_form_class(related_fields=["nutrition_set"])

    def test_nullable_fk_is_accepted(self):
        form = self.get_form_class(related_fields=["price_set"])()
        self.assertIn("price_set", form.fields)

    def test_form_save_regular_m2m_fields(self):
        Form = reverse_relationship_form_factory(
            models.Pizza, fields=["name", "toppings"]
        )
        form = Form({"name": "California", "toppings": [self.mushrooms.pk]})
        california = form.save()
        self.assertQuerySetEqual(california.toppings.all(), [self.mushrooms])


class ReverseRelationshipAdminTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_superuser(username="test")
        self.client.force_login(self.user)

    def test_add_form_renders_related_field(self):
        res = self.client.get(reverse("admin:tests_topping_add"))
        self.assertContains(res, '<select name="pizza_set"')

    def test_change_form_renders_related_field(self):
        res = self.client.get(
            reverse("admin:tests_topping_change", args=[self.mushrooms.pk])
        )
        self.assertContains(res, '<select name="pizza_set"')

    def test_add_form_saves_related_fields(self):
        self.client.post(
            reverse("admin:tests_topping_add"),
            {"name": "Peppers", "pizza_set": [self.veggie.pk]},
        )
        peppers = models.Topping.objects.get(name="Peppers")
        self.assertQuerySetEqual(peppers.pizza_set.all(), [self.veggie])

    def test_change_form_saves_related_fields(self):
        self.client.post(
            reverse("admin:tests_topping_change", args=[self.mushrooms.pk]),
            {"name": "Peppers", "pizza_set": [self.mediterranean.pk]},
        )
        peppers = models.Topping.objects.get(name="Peppers")
        self.assertQuerySetEqual(peppers.pizza_set.all(), [self.mediterranean])

    def test_default_related_queryset(self):
        ToppingAdmin.related_querysets = None
        res = self.client.get(reverse("admin:tests_topping_add"))
        self.assertContains(res, '<option value="1">Veggie</option>')
        self.assertContains(res, '<option value="2">Mediterranean</option>')

    def test_custom_related_querset(self):
        ToppingAdmin.related_querysets = {
            "pizza_set": models.Pizza.objects.filter(name__istartswith="v")
        }
        res = self.client.get(reverse("admin:tests_topping_add"))
        self.assertContains(res, '<option value="1">Veggie</option>')
        self.assertNotContains(res, '<option value="2">Mediterranean</option>')

    def test_custom_related_labels(self):
        ToppingAdmin.related_labels = {"pizza_set": "Pizza selection"}
        res = self.client.get(reverse("admin:tests_topping_add"))
        self.assertContains(res, '<label for="id_pizza_set">Pizza selection:</label>')

    def test_default_reverse_m2m_widget(self):
        ToppingAdmin.related_filter_horizontal = None
        ToppingAdmin.related_filter_vertical = None
        res = self.client.get(reverse("admin:tests_topping_add"))
        widget = res.context["adminform"].form.fields["pizza_set"].widget
        self.assertIsInstance(widget, RelatedFieldWidgetWrapper)
        self.assertIsInstance(widget.widget, SelectMultiple)

    def test_filter_horizontal(self):
        ToppingAdmin.related_filter_horizontal = ["pizza_set"]
        ToppingAdmin.related_filter_vertical = None
        res = self.client.get(reverse("admin:tests_topping_add"))
        widget = res.context["adminform"].form.fields["pizza_set"].widget
        self.assertIsInstance(widget, RelatedFieldWidgetWrapper)
        self.assertFalse(widget.widget.is_stacked)

    def test_filter_vertical(self):
        ToppingAdmin.related_filter_horizontal = None
        ToppingAdmin.related_filter_vertical = ["pizza_set"]
        res = self.client.get(reverse("admin:tests_topping_add"))
        widget = res.context["adminform"].form.fields["pizza_set"].widget
        self.assertIsInstance(widget, RelatedFieldWidgetWrapper)
        self.assertTrue(widget.widget.is_stacked)

    def test_filter_horizontal_for_m2m(self):
        res = self.client.get(reverse("admin:tests_pizza_add"))
        widget = res.context["adminform"].form.fields["toppings"].widget
        self.assertIsInstance(widget, RelatedFieldWidgetWrapper)
        self.assertIsInstance(widget.widget, FilteredSelectMultiple)
        self.assertFalse(widget.widget.is_stacked)

    def test_invalid_related_field(self):
        related_fields = ToppingAdmin.related_fields
        ToppingAdmin.related_fields = ["foo"]
        with self.assertRaises(FieldError):
            self.client.get(reverse("admin:tests_topping_add"))
        ToppingAdmin.related_fields = related_fields
