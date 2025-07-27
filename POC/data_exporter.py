import pandas as pd
import json
from utils import log_info, log_error

def export_to_csv(data, filename='imdb_movies.csv', encoding='utf-8'):
    """
    Exporta datos a formato CSV
    params:
        data: list -> lista de diccionarios con datos
        filename: str -> nombre del archivo de salida
        encoding: str -> encoding del archivo
    returns:
        bool -> True si se exportó correctamente, False en caso contrario
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding=encoding)
        log_info(f"Datos exportados exitosamente a {filename}")
        return True
    except Exception as e:
        log_error(f"Error al exportar a CSV {filename}: {e}")
        return False

def export_to_json(data, filename='imdb_movies.json', encoding='utf-8'):
    """
    Exporta datos a formato JSON
    params:
        data: list -> lista de diccionarios con datos
        filename: str -> nombre del archivo de salida
        encoding: str -> encoding del archivo
    returns:
        bool -> True si se exportó correctamente, False en caso contrario
    """
    try:
        with open(filename, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log_info(f"Datos exportados exitosamente a {filename}")
        return True
    except Exception as e:
        log_error(f"Error al exportar a JSON {filename}: {e}")
        return False

def export_to_excel(data, filename='imdb_movies.xlsx'):
    """
    Exporta datos a formato Excel
    params:
        data: list -> lista de diccionarios con datos
        filename: str -> nombre del archivo de salida
    returns:
        bool -> True si se exportó correctamente, False en caso contrario
    """
    try:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False, engine='openpyxl')
        log_info(f"Datos exportados exitosamente a {filename}")
        return True
    except Exception as e:
        log_error(f"Error al exportar a Excel {filename}: {e}")
        return False

def export_data(data, formats=['csv'], base_filename='imdb_movies'):
    """
    Exporta datos a múltiples formatos
    params:
        data: list -> lista de diccionarios con datos
        formats: list -> lista de formatos a exportar ['csv', 'json', 'excel']
        base_filename: str -> nombre base del archivo
    returns:
        dict -> diccionario con el resultado de cada exportación
    """
    results = {}
    
    for format_type in formats:
        if format_type == 'csv':
            filename = f"{base_filename}.csv"
            results['csv'] = export_to_csv(data, filename)
        elif format_type == 'json':
            filename = f"{base_filename}.json"
            results['json'] = export_to_json(data, filename)
        elif format_type == 'excel':
            filename = f"{base_filename}.xlsx"
            results['excel'] = export_to_excel(data, filename)
        else:
            log_error(f"Formato no soportado: {format_type}")
            results[format_type] = False
    
    return results

def get_data_summary(data):
    """
    Genera un resumen de los datos extraídos
    params:
        data: list -> lista de diccionarios con datos
    returns:
        dict -> resumen de los datos
    """
    if not data:
        return {"total_movies": 0}
    
    summary = {
        "total_movies": len(data),
        "movies_with_rating": len([m for m in data if m.get('rating') and m.get('rating') != 'N/A']),
        "movies_with_duration": len([m for m in data if m.get('duration')]),
        "movies_with_actors": len([m for m in data if m.get('actors') and len(m.get('actors', [])) > 0]),
        "movies_with_metascore": len([m for m in data if m.get('metascore') and m.get('metascore') != 'N/A']),
        "average_rating": None,
        "year_range": None
    }
    
    # Calcular rating promedio
    ratings = [float(m.get('rating', 0)) for m in data if m.get('rating') and m.get('rating') != 'N/A' and m.get('rating').replace('.', '').isdigit()]
    if ratings:
        summary["average_rating"] = sum(ratings) / len(ratings)
    
    # Calcular rango de años
    years = [int(m.get('year', 0)) for m in data if m.get('year') and m.get('year') != 'N/A' and m.get('year').isdigit()]
    if years:
        summary["year_range"] = f"{min(years)} - {max(years)}"
    
    return summary 