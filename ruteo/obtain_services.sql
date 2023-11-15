SELECT
servicio."observacionesOperador" OBSERVACIONES,
estado_servicio.id ESTADO_SERVICIO,
servicio.id SERVICIO_ID,
cliente.id CLIENTE_ID,
pasajero.numero_documento IDENTIFICACION_USUARIO,
pasajero.primer_nombre || ' ' || pasajero.primer_apellido as NOMBRE_USUARIO,
categoria_pasajero.id CRITICIDAD,
medio_apoyo.id MEDIO_DE_APOYO,
to_char(servicio."fechaServicio" AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD') AS fecha_servicio,
to_char(servicio."fechaServicio" AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota', 'HH24:MI:SS') AS HORA_SERVICIO,
regional_origen.id regional_id_origen,
ciudad_origen.id ciudad_id_origen,
ciudad_origen.nombre ciudad_origen,
localidad_origen.nombre localidad_origen,
upz_origen.nombre upz_origen,
barrio_origen.nombre barrio_origen,
origen.direccion direccion_origen,
origen.descripcion descripcion_origen,
regional_destino.id regional_id_destino,
ciudad_destino.id ciudad_id_destino,
ciudad_destino.nombre ciudad_destino,
localidad_destino.nombre localidad_destino,
upz_destino.nombre upz_destino,
barrio_origen.nombre barrio_origen,
destino.direccion direccion_destino,
destino.descripcion descripcion_destino,
tipo_ruta.id tipo_ruta,
origen.latitude latitud_origen,
origen.longitude longitud_origen,
destino.latitude latitud_destino,
destino.longitude longitud_destino,
pasajero."telefono_Celular1" celular_1,
pasajero."telefono_Celular1" celular_2,
case when servicio.detalle then 'Ida' else 'Retorno' end detalle_servicio
from public.servicios_servicio servicio
LEFT JOIN public.servicios_estadoservicio estado_servicio ON servicio."codigoServicio_id" = estado_servicio.id
LEFT JOIN public.servicios_tiporuta tipo_ruta ON servicio."tipoRuta_id" = tipo_ruta.id
LEFT JOIN public.pasajeros_pasajero pasajero on servicio.pasajero_id = pasajero.id
LEFT JOIN public.clientes_cliente cliente on pasajero.cliente_id = cliente.id
LEFT JOIN public.pasajeros_categoriapasajero categoria_pasajero on pasajero."categoria_Pasajero_id" = categoria_pasajero.id
LEFT JOIN public."mediosApoyo_medioapoyo" medio_apoyo ON pasajero.medio_id = medio_apoyo.id
LEFT JOIN public.destinos_destino destino on servicio.destino_id = destino.id
LEFT JOIN public.general_barrio barrio_destino on destino.barrio_id = barrio_destino.id
LEFT JOIN public.general_upz upz_destino on barrio_destino."Upz_id" = upz_destino.id
LEFT JOIN public.general_localidad localidad_destino on upz_destino."Localidad_id" = localidad_destino.id
LEFT JOIN public.general_ciudad ciudad_destino on localidad_destino."Ciudad_id" = ciudad_destino.id 
LEFT JOIN public.general_departamento regional_destino on ciudad_destino."Departamento_id" = regional_destino.id
LEFT JOIN public.destinos_destino origen on servicio.origen_id = origen.id
LEFT JOIN public.general_barrio barrio_origen on origen.barrio_id = barrio_origen.id
LEFT JOIN public.general_upz upz_origen on barrio_origen."Upz_id" = upz_origen.id
LEFT JOIN public.general_localidad localidad_origen on upz_origen."Localidad_id" = localidad_origen.id
LEFT JOIN public.general_ciudad ciudad_origen on localidad_origen."Ciudad_id" = ciudad_origen.id
LEFT JOIN public.general_departamento regional_origen on ciudad_origen."Departamento_id" = regional_origen.id 
WHERE
DATE(servicio."fechaServicio" AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota') >= '{0}'
AND DATE(servicio."fechaServicio" AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota') <= '{1}'
AND medio_id != 25 -- Medio de apoyo no rampa
AND "tipoProcedimiento_id" in ({2})
AND "estadoServicio_id" in (3, 4, 5, 6, 7, 8, 9, 21, 22, 23, 24)