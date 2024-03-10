from django.contrib.auth import get_user_model
from django.forms.models import ALL_FIELDS
from django.test import TestCase
from django.urls import reverse

from . import models
from reverse_relationship_form.forms import reverse_relationship_form_factory


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
