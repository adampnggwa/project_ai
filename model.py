from tortoise import fields
from tortoise.models import Model
from tortoise.fields import DatetimeField

class User(Model):
    user_id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100, unique=True)
    token = fields.CharField(max_length=500, null=True)
    token_expiration = fields.DatetimeField(null=True)
    password = fields.CharField(max_length=564, null=True)
    image_count = fields.IntField(default=0)
    last_image_generated_at = fields.DatetimeField(null=True)
    generated_images = fields.ReverseRelation["GeneratedImage"]

    class Meta:
        table = "users"
        
    def __str__(self):
        return self.user_id
    
class GeneratedImage(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='generated_images')
    image_url = fields.CharField(max_length=500)  
    prompt = fields.TextField()  
    created_at = DatetimeField(auto_now_add=True)

    class Meta:
        table = "generated_images"

    def __str__(self):
        return self.id