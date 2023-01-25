def find_differences(old_obj, updated_obj):
    old_values = [(k,v) for k,v in old_obj.__dict__.items() if k != '_state']
    new_values = [(k,v) for k,v in updated_obj.__dict__.items() if k != '_state']
    diff = [f for f in new_values if f not in old_values]
    return diff