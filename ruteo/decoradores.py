def contador(func):
    """
        Decorador que realiza un seguimiento del número de veces
            que se llama una función.

        Args:
            func (function): La función a la que se aplicará el contador.

        Returns:
            function: Una función envoltorio que realiza el seguimiento
                de las llamadas y proporciona un método para obtener los recuentos.
    """
    counts = {}  # Diccionario para almacenar el recuento de cada función

    def wrapper(*args, **kwargs):
        """
            Función envoltorio que realiza el seguimiento de las
                llamadas a la función y devuelve su resultado.

            Args:
                *args: Argumentos posicionales para la función.
                **kwargs: Argumentos clave para la función.

            Returns:
                Any: El resultado de la función original.
        """
        counts[func.__name__] = counts.get(func.__name__, 0) + 1
        result = func(*args, **kwargs)
        return result

    def get_counts():
        """
            Obtiene el diccionario de recuentos de llamadas a las funciones.

            Returns:
                dict: Un diccionario que contiene el recuento de
                    llamadas para cada función decorada.
        """
        return counts
    wrapper.get_counts = get_counts
    return wrapper
