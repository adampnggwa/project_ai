from datetime import datetime
import pytz

async def reset_points(user):
    current_time = datetime.now(pytz.utc)
    if user.last_login is None:
        user.last_login = datetime.now(pytz.utc)
        await user.save()
    point_reset = user.last_login.date() < current_time.date()
    if point_reset:
        user.points = 50
        if user.premium:
            user.points = 120
        user.last_login = current_time
        await user.save()

async def points_calculation(user, action_name, size=None):    
    if action_name == 'generate-image':
        size_points = {
            'small': 1,
            'medium': 3,
            'large': 5
        }
        if size in size_points and user.points >= size_points[size]:
            user.points -= size_points[size]
            await user.save()
            return True 
        else:
            return False
    elif action_name in ('edit-image', 'generate-variation'):
        if user.points >= 5:
            user.points -= 5
            await user.save()
            return True 
        else:
            return False   