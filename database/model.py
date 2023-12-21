from tortoise import fields
from tortoise.models import Model
from tortoise.fields import DatetimeField

class userdata(Model):
    user_id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100)
    password = fields.BinaryField(max_length=564, null=True)
    google_auth = fields.BooleanField(default=False)
    verified = fields.BooleanField(default=False)
    verification_token = fields.CharField(max_length=100, null=True)
    verification_token_expiration = fields.DatetimeField(null=True)
    points = fields.IntField(default=0)
    last_login = fields.DatetimeField(null=True)
    premium = fields.BooleanField(default=False)
    premium_expiration = DatetimeField(null=True)

    class Meta:
        table = "userdata"
        
    def __str__(self):
        return self.user_id

class buyerdata(Model):
    user_id = fields.IntField()
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    address_line = fields.CharField(max_length=255, null=True)
    city = fields.CharField(max_length=255, null=True)
    region = fields.CharField(max_length=255, null=True)
    postcode = fields.CharField(max_length=20, null=True)
    country = fields.CharField(max_length=100, null=True)

    class Meta:
        table = "buyer_data"
        
    def __str__(self):
        return self.user_id
    
class PaymentTransaction(Model):
    transaction_id = fields.IntField(pk=True)
    user_id = fields.IntField()
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    payment_status = fields.CharField(max_length=20, default=False)
    payment_method = fields.CharField(max_length=50)
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "payment_transaction"

    def __str__(self):
        return self.transaction_id
    
class accesstoken(Model):
    user_id = fields.IntField()
    token = fields.CharField(max_length=500, null=True)
    token_expiration = fields.DatetimeField(null=True)

    class Meta:
        table = "access_token"
        
    def __str__(self):
        return self.user_id
    
class GeneratedImage(Model):
    id = fields.IntField(pk=True)
    image_url = fields.CharField(max_length=500)  
    prompt = fields.TextField()  
    size = fields.CharField(max_length=50)
    created_at = DatetimeField(auto_now_add=True)

    class Meta:
        table = "generated_images"

    def __str__(self):
        return self.id

class EditedImage(Model):
    id = fields.IntField(pk=True)
    image_url = fields.CharField(max_length=500)  
    prompt = fields.TextField()  
    created_at = DatetimeField(auto_now_add=True)

    class Meta:
        table = "edited_images"

    def __str__(self):
        return self.id
    
class GeneratedVariation(Model):
    id = fields.IntField(pk=True)
    image_url = fields.CharField(max_length=500)    
    created_at = DatetimeField(auto_now_add=True)

    class Meta:
        table = "generated_variations"

    def __str__(self):
        return self.id