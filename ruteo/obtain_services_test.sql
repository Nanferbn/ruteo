SELECT
servicio.id SERVICIO_ID,
pasajero.numero_documento IDENTIFICACION_USUARIO,
pasajero.primer_nombre || ' ' || pasajero.primer_apellido as NOMBRE_USUARIO,
to_char(servicio."fechaServicio" AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD') AS FECHA_SERVICIO,
to_char(servicio."fechaServicio" AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota', 'HH24:MI:SS') AS HORA_SERVICIO,
ciudad_origen.id ciudad_id_origen,
ciudad_origen.nombre ciudad_origen,
localidad_origen.nombre localidad_origen,
upz_origen.nombre upz_origen,
barrio_origen.nombre barrio_origen,
origen.direccion direccion_origen,
origen.descripcion descripcion_origen,
ciudad_destino.id ciudad_id_destino,
ciudad_destino.nombre ciudad_destino,
localidad_destino.nombre localidad_destino,
upz_destino.nombre upz_destino,
barrio_origen.nombre barrio_origen,
destino.direccion direccion_destino,
destino.descripcion descripcion_destino,
origen.latitude latitud_origen,
origen.longitude longitud_origen,
destino.latitude latitud_destino,
destino.longitude longitud_destino,
CASE WHEN servicio.detalle THEN 'Ida' ELSE 'Retorno' END detalle_servicio
FROM sangabriel_08052023.public.servicios_servicio servicio
LEFT JOIN sangabriel_08052023.public.servicios_estadoservicio estado_servicio ON servicio."codigoServicio_id" = estado_servicio.id
LEFT JOIN sangabriel_08052023.public.pasajeros_pasajero pasajero ON servicio.pasajero_id = pasajero.id
LEFT JOIN sangabriel_08052023.public.destinos_destino destino ON servicio.destino_id = destino.id
LEFT JOIN sangabriel_08052023.public.general_barrio barrio_destino ON destino.barrio_id = barrio_destino.id
LEFT JOIN sangabriel_08052023.public.general_upz upz_destino ON barrio_destino."Upz_id" = upz_destino.id
LEFT JOIN sangabriel_08052023.public.general_localidad localidad_destino ON upz_destino."Localidad_id" = localidad_destino.id
LEFT JOIN sangabriel_08052023.public.general_ciudad ciudad_destino ON localidad_destino."Ciudad_id" = ciudad_destino.id 
LEFT JOIN sangabriel_08052023.public.destinos_destino origen ON servicio.origen_id = origen.id
LEFT JOIN sangabriel_08052023.public.general_barrio barrio_origen ON origen.barrio_id = barrio_origen.id
LEFT JOIN sangabriel_08052023.public.general_upz upz_origen ON barrio_origen."Upz_id" = upz_origen.id
LEFT JOIN sangabriel_08052023.public.general_localidad localidad_origen ON upz_origen."Localidad_id" = localidad_origen.id
LEFT JOIN sangabriel_08052023.public.general_ciudad ciudad_origen ON localidad_origen."Ciudad_id" = ciudad_origen.id 
WHERE
DATE(servicio."fechaServicio" AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota') >= '{0}'
AND DATE(servicio."fechaServicio" AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota') <= '{1}'
AND medio_id != 25 -- Medio de apoyo no rampa
AND "tipoProcedimiento_id" = {2} --14 -- Dialisis
AND "estadoServicio_id" in (3, 4, 5, 6, 7, 8, 9, 21, 22, 23, 24)