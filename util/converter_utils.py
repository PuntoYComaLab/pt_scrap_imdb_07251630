def convert_duration_to_minutes(duration_str):
    """
    Convierte duración de formato "1h 30m" a minutos
    params:
        duration_str: str -> duración en formato "1h 30m"
    returns:
        int -> duración en minutos, None si no se puede convertir
    """
    if not duration_str:
        return None
    
    total_minutes = 0
    if 'h' in duration_str:
        hours_str = duration_str.split('h')[0].strip()
        total_minutes += int(hours_str) * 60
        duration_str = duration_str.split('h')[1].strip()
    if 'm' in duration_str:
        minutes_str = duration_str.replace('m', '').strip()
        total_minutes += int(minutes_str)
    return total_minutes if total_minutes > 0 else None 