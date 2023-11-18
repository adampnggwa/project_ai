from datetime import datetime, timedelta
import pytz

user_action_tracker = {}

def reset_user_points(user):
    now = datetime.now(pytz.utc)
    now_timestamp = now.timestamp()
    if user.user_id in user_action_tracker:
        last_reset_time = user_action_tracker[user.user_id].get('points_timestamp', 0)
        if now_timestamp - last_reset_time > timedelta(days=1).total_seconds():
            user_action_tracker[user.user_id]['points_timestamp'] = now_timestamp
            user.points = 50
            if user.premium :
                user.points = 120
                return True
            return True
    else:
        user_action_tracker[user.user_id] = {'points_timestamp': now_timestamp}
        user.points = 50
        if user.premium :
            user.points = 120
            return False
    return False

def can_use_action(user, action_name, size=None):
    if reset_user_points(user):
        return True    
    if action_name == 'generate-image':
        size_points = {
            'small': 1,
            'medium': 3,
            'large': 5
        }
        if size in size_points and user.points >= size_points[size]:
            user.points -= size_points[size]
            return True    
    elif action_name in ('edit-image', 'generate-variation'):
        if user.points >= 5:
            user.points -= 5
            return True    
    return False