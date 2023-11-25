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