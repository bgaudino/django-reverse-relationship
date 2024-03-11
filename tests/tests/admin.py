from django.contrib import admin

from reverse_relationship_form.admin import ReverseRelationshipAdmin

from . import models


@admin.register(models.Pizza)
class PizzaAdmin(ReverseRelationshipAdmin):
    filter_horizontal = ["toppings"]


@admin.register(models.Topping)
class ToppingAdmin(ReverseRelationshipAdmin):
    related_fields = ["pizza_set"]
    related_filter_horizontal = ["pizza_set"]
