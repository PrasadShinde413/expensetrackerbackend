from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    
    USERNAME_FIELD = 'email'
    objects = BaseUserManager()

class TempUser(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=255) # Hashed
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    TYPE_CHOICES = [('income', 'Income'), ('expense', 'Expense')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    class Meta:
        unique_together = ('user', 'name', 'type')

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=[('income', 'Income'), ('expense', 'Expense')])
    date = models.DateField()
    description = models.TextField(blank=True)

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    limit = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.IntegerField() # 1-12
    year = models.IntegerField()