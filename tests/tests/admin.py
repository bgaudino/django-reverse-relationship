from django.contrib import admin

from reverse_relationship.admin import ReverseRelationshipAdmin

from . import models


@admin.register(models.Pizza)
class PizzaAdmin(ReverseRelationshipAdmin):
    filter_horizontal = ["toppings"]


@admin.register(models.Topping)
class ToppingAdmin(ReverseRelationshipAdmin):
    related_fields = ["pizza_set", "price_set"]
    related_filter_horizontal = ["pizza_set", "price_set"]


@admin.register(models.Price)
class PriceAdmin(admin.ModelAdmin):
    pass
