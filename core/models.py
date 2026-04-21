from django.db import models

class Carousel(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    image = models.ImageField(upload_to='media')
    marked_price = models.PositiveIntegerField()
    discount = models.IntegerField() 
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.price = self.marked_price * (1 - self.discount / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class New_Arrivals(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    image = models.ImageField(upload_to='media')
    marked_price = models.PositiveIntegerField()

    def __str__(self):
        return self.title
    
class Non_Fiction(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    image = models.ImageField(upload_to='media')
    marked_price = models.PositiveIntegerField()

    def __str__(self):
        return self.title
    
class Fiction(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    image = models.ImageField(upload_to='media')
    marked_price = models.PositiveIntegerField()

    def __str__(self):
        return self.title
    
class Nepali(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    image = models.ImageField(upload_to='media')
    marked_price = models.PositiveIntegerField()

    def __str__(self):
        return self.title
    
class Best_Sellers(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    image = models.ImageField(upload_to='media')
    marked_price = models.PositiveIntegerField()

    def __str__(self):
        return self.title
    
class Cart(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('new_arrival', 'New Arrival'),
        ('best_seller', 'Best Seller'),
    ]
    product_id = models.PositiveIntegerField()
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    image = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    session_key = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} ({self.session_key})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    session_key = models.CharField(max_length=100)
    total_amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"
    
class Payments(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    session_key = models.CharField(max_length=100)
    total_amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"
    
class Order(models.Model):
    session_key = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)  # ← add this if missing