# Django Reverse Relationship
[![Tests](https://github.com/bgaudino/django-reverse-relationship/actions/workflows/tests.yml/badge.svg)](https://github.com/bgaudino/django-reverse-relationship/actions/workflows/tests.yml)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## Rationale  
Have you ever needed to manage a `ManyToManyField` on both sides of the relationship in the admin and found out that Django does not make this easy?

### Example:  
Consider the following models:

```python
from django.contrib import admin
from django.db import models

class Topping(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Pizza(models.Model):
    name = models.CharField(max_length=255)
    toppings = models.ManyToManyField(Topping, related_name="pizzas")

    def __str__(self):
        return self.name


@admin.register(models.Pizza)
class PizzaAdmin(admin.ModelAdmin):
    fields = ["name", "toppings"]
    filter_horizontal = ["toppings"]


@admin.register(models.Topping)
class ToppingAdmin(ReverseRelationshipAdmin):
    fields = ["name", "pizzas"]
    filter_horizontal = ["pizzas"]

```

In this example, you can easily add the `toppings` field to `PizzaAdmin`, but trying to add `pizzas` to `ToppingAdmin` will raise the following error:

```
Unknown field(s) (pizzas) specified for Topping
```

This package solves this problem by providing the `ReverseRelationshipAdmin`:

```python
from reverse_relationship.admin import ReverseRelationshipAdmin
from .models import Topping

@admin.register(Topping)
class ToppingAdmin(ReverseRelationshipAdmin):
    fields = ["name"]
    related_fields = ["pizzas"]
    related_filter_horizontal = ["pizzas"]
```

## Customization

The following attributes can be used to customize the `ReverseRelationshipAdmin` class.

### `related_querysets`
You can customize the queryset for related fields by passing a dictionary to `related_querysets`, where keys are the field names and values are the `QuerySet` instances. This allows you to limit the available options in the reverse relationships.

```python
related_querysets = {
    "pizzas": Pizza.objects.filter(name__startswith="veggie"),
}
```

### `related_filter_horizontal` / `related_filter_vertical`
Use these options to display reverse fields with Django’s `FilteredSelectMultipleField` widget, either horizontally or vertically.

```python
related_filter_horizontal = ["pizzas"]
```

### `related_labels`
You can specify custom labels for reverse relationships.

```python
related_labels = {
    "pizzas": "Available Pizzas",
}
```

### Hooks
Each of these attributes has a hook available (eg. `get_related_querysets`) than can be overwritten to customize the value based on the request object and/or model instance.

## Use Outside of Admin
Use `reverse_relationship_form_factory` to create model forms with reverse relationships anywhere in your Django app.

```python
from reverse_relationship.forms import reverse_relationship_form_factory 
from .models import Topping

ToppingForm = reverse_relationship_form_factory(
    model=Topping,
    related_fields=["pizzas"],
)
```

The generated HTML form will look like this:

```html
<div>
    <label for="id_name">Name:</label>
    <input type="text" name="name" maxlength="255" required id="id_name">
</div>
<div>
    <label for="id_pizzas">Pizzas:</label>
    <select name="pizzas" id="id_pizzas" multiple>
        <!-- Whatever pizzas are in your database -->
        <option value="1">Veggie</option>
        <option value="2">Cheese</option>
        <option value="3">Mediterranean</option>
    </select>
</div>
```

# Limitations
While primarily designed for ManyToManyField relationships, this package also supports ForeignKey relationships, but only if the foreign key is nullable.