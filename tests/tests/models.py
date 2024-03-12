from django.db import models


class Topping(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Pizza(models.Model):
    name = models.CharField(max_length=255)
    toppings = models.ManyToManyField(Topping, blank=True)

    def __str__(self):
        return self.name


class Nutrition(models.Model):
    topping = models.ForeignKey(Topping, on_delete=models.CASCADE)


class Price(models.Model):
    topping = models.ForeignKey(Topping, on_delete=models.CASCADE, null=True)
