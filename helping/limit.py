import time

user_action_tracker = {}

def can_use_action(user_id, action_name):
    now = time.time()
    if user_id not in user_action_tracker:
        user_action_tracker[user_id] = {}    
    if action_name not in user_action_tracker[user_id]:
        user_action_tracker[user_id][action_name] = {'count': 0, 'timestamp': now}
    action_info = user_action_tracker[user_id][action_name]
    if now - action_info['timestamp'] > 3600: 
        action_info['count'] = 0
        action_info['timestamp'] = now
    if action_info['count'] < 3:
        action_info['count'] += 1
        action_info['timestamp'] = now
        return True
    else:
        return False