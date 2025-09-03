combat_log = []

def add_log(message):
    combat_log.append(message)
    if len(combat_log) > 5:
        combat_log.pop(0)
