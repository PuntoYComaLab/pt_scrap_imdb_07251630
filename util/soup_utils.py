def safe_get_text(element, default='N/A'):
    """
    Extrae texto de un elemento BeautifulSoup de forma segura
    params:
        element: BeautifulSoup element -> elemento a extraer texto
        default: str -> valor por defecto si no se encuentra
    returns:
        str -> texto extraído o valor por defecto
    """
    if element and element.text:
        return element.text.strip()
    return default

def safe_get_attribute(element, attribute, default=None):
    """
    Extrae atributo de un elemento BeautifulSoup de forma segura
    params:
        element: BeautifulSoup element -> elemento a extraer atributo
        attribute: str -> nombre del atributo
        default: any -> valor por defecto si no se encuentra
    returns:
        any -> valor del atributo o valor por defecto
    """
    if element and hasattr(element, 'attrs') and attribute in element.attrs:
        return element.attrs[attribute]
    return default 