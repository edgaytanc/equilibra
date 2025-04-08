def analizar_mensaje(texto):
    """
    Funcion dummy para analizar el contenido de un mensaje.
    Devuelve un diccionario con el nivel de estres y sentimiento.
    """
    
    texto_lower = texto.lower()

    if "estresado" in texto_lower or "estresada" in texto_lower:
        return {
            "nivel_estres": "alto",
            "sentimiento": "negativo"
        }
    elif "feliz" in texto_lower or "contento" in texto_lower:
        return {
            "nivel_estres": "bajo",
            "sentimiento": "positivo"
        }
    else:
        return {
            "nivel_estres": "moderado",
            "sentimiento": "neutral"
        }