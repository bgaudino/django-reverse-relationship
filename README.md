# Django Reverse Relationship Form
[![Tests](https://github.com/bgaudino/django-reverse-relationship-form/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/bgaudino/django-reverse-relationship-form/actions/workflows/tests.yml)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>



Have you ever needed to be able to set a `ManyToManyField` field on the *other* side of the relationship in your forms or admin? That's what this package does.

## Forms

Say you have the following models.


```python
from django.db import models


class Topping(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Pizza(models.Model):
    name = models.CharField(max_length=255)
    toppings = models.ManyToManyField(Topping)

    def __str__(self):
        return self.name

```

A model form for Pizza would include a `MultipleModelSelectField` but a model form for topping would not. Enter, `reverse_relationship_form_factory`. Notice that because I didn't set a related name for `toppings`, I'm using Django's default of the child model name + '_set'. If you specified a related name, you would list that under `related_fields` instead.


```python
from reverse_relationship_form.forms import reverse_relationship_form_factory 

from .models import Topping

ToppingForm = reverse_relationship_form_factory(
    model=Topping,
    related_fields=["pizza_set"],
)
```

The resulting HTML form, generated by `ToppingForm.render()`, would resemble the following:

```html
<div>
    <label for="id_name">Name:</label>
    <input type="text" name="name" maxlength="255" required id="id_name">
</div>
<div>
    <label for="id_pizza_set">Pizzas:</label>
    <select name="pizza_set" id="id_pizza_set" multiple>
        <!--Whatever pizzas are in your database-->
        <option value="1">Veggie</option>
        <option value="2">Cheese</option>
        <option value="3">Mediterranean</option>
    </select>
</div>
```

`reverse_relationship_form_factory` calls Django's `model_form_factory` and passes along all the same kwargs, so you can set your labels, widgets, etc. It also accepts a `related_querysets` kwarg so you can limit the choices for related fields. `related_querysets` expects a dictionary with field names as keys and `Queryset` instances as values.

## Admin

Adding reverse related fields is easy. Just use `ReverseRelationshipAdmin`.

```python
from reverse_relationship_form.admin import ReverseRelationshipAdmin

from .models import Topping


@admin.register(Topping)
class ToppingAdmin(ReverseRelationshipAdmin):
    related_fields = ["pizza_set"]
    related_filter_horizontal = ["pizza_set"]
```

Specifying a related field as `related_filter_horizontal` or `related_filter_vertical` uses Django's nice `FilteredSelectMultipleField`.

## Limitations

While primarily designed for many-to-many relationships, this package can be used for many-to-one relationships if the `ForeignKey` field on the other side is nullable. Removing a model instance from the select widget sets the foreign key field to null, so if it's not nullable you can't remove it.
