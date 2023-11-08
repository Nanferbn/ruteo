from ruta import servicios_completos


if __name__ == '__main__':
    df_rutas_ida, df_rutas_retorno = servicios_completos(
        '2023-04-05', '2023-04-06', [14], 30)
    # fecha_inicio, fecha_final,
    # tipo_de_procedimiento_id, tiempo_máximo_estimado
    df_rutas_ida.to_excel("rutas_ida_agosto.xlsx", index=False)
    df_rutas_retorno.to_excel("rutas_retorno_agosto.xlsx", index=False)
