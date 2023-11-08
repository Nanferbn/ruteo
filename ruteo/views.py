from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from apps.usuarios.views import user_validar_rol
from apps.ruteo.ruta import servicios_completos
from apps.procedimientos.forms import *
from apps.procedimientos.models import *
from apps.destinos.models import *
import os
from flask import Flask, send_file, render_template, make_response
import xlsxwriter
import pandas as pd
import json
from pandas import json_normalize
import openpyxl
from io import BytesIO

def consultaRutas(request):
	ciudades = Ciudad.objects.all().order_by('nombre').select_related()
	departamentos = Departamento.objects.all().order_by('nombre').select_related()
	procedimientos = Procedimiento.objects.filter(id=14)
	context={
		'departamentos': departamentos,
		'ciudades': ciudades,
		'procedimientos': procedimientos,
		'showProgramacion': 'show',
		'activeProgramacion': 'active',
		'activeProgramacion': 'active'
	}
	fecha_inicio = request.GET.get('startDateSevice')
	fecha_fin = request.GET.get('endDateSevice')
	tiempo = request.GET.get('tiempo')
	tipo_procedimiento = request.GET.get('tipo_procedimiento')
	ciudad_origen = request.GET.get('ciudad_origen')
	ciudad_destino = request.GET.get('ciudad_destino')
	print("-----------------", fecha_inicio, fecha_fin, tipo_procedimiento, ciudad_origen, ciudad_destino)	
	if request.method=='GET':
		if request.GET.get('action') == 'download':
			output = BytesIO()			
			df_rutas_ida, df_rutas_retorno = servicios_completos(
				fecha_inicio, fecha_fin, [14], int(tiempo))
			columnas_omitidas = [
				'IDENTIFICACION_USUARIO',
				'HORA_SERVICIO_C',
				'LATITUD_ORIGEN',
				'LONGITUD_ORIGEN',
				'LATITUD_DESTINO',
				'LONGITUD_DESTINO',
				'GRUPO_DESTINO',
				'GRUPO_HORA',
				'RUTA_PREVIA',
				'RUTA_INICIAL',
				'DISTANCIA_LINEAL',
				'COORD_ORIGEN',
				'COORD_DESTINO',
			]
			df_rutas_ida_export = df_rutas_ida.drop(columns=columnas_omitidas, axis=1, errors='ignore')
			df_rutas_retorno_export = df_rutas_retorno.drop(columns=columnas_omitidas, axis=1, errors='ignore')
			columnas_ordenadas = [
				'OBSERVACIONES',
				'ESTADO_SERVICIO',
				'SERVICIO_ID',
				'CLIENTE_ID',
				'CRITICIDAD',
				'MEDIO_DE_APOYO',				
				'FECHA_SERVICIO',	
				'HORA_SERVICIO',
				'REGIONAL_ID_ORIGEN',
				'CIUDAD_ID_ORIGEN',
				'CIUDAD_ORIGEN',
				'LOCALIDAD_ORIGEN',
				'DIRECCION_ORIGEN',
				'UPZ_ORIGEN',
				'BARRIO_ORIGEN',	
				'DESCRIPCION_ORIGEN',
				'REGIONAL_ID_DESTINO',
				'CIUDAD_ID_DESTINO',
				'CIUDAD_DESTINO',
				'LOCALIDAD_DESTINO',
				'UPZ_DESTINO',
				'DIRECCION_DESTINO',
				'DESCRIPCION_DESTINO',
				'NOMBRE_USUARIO',
				'CELULAR_1',
				'CELULAR_2',
				'RUTA_FINAL',
			]			
			df_rutas_ida_ciudades_filter = df_rutas_ida_export[(df_rutas_ida_export['CIUDAD_ID_ORIGEN'] == int(ciudad_origen)) & (df_rutas_ida_export['CIUDAD_ID_DESTINO'] == int(ciudad_destino))]
			df_rutas_retorno_ciudades_filter = df_rutas_retorno_export[(df_rutas_retorno_export['CIUDAD_ID_ORIGEN'] == int(ciudad_origen)) & (df_rutas_retorno_export['CIUDAD_ID_DESTINO'] == int(ciudad_destino))]

			df_rutas_ida_ciudades_filter = df_rutas_ida_ciudades_filter[columnas_ordenadas]	
			df_rutas_retorno_ciudades_filter = df_rutas_retorno_ciudades_filter[columnas_ordenadas]

			writer = pd.ExcelWriter(output, engine='xlsxwriter')
			df_rutas_ida_ciudades_filter.to_excel(writer, sheet_name='Rutas ida', index=False)
			df_rutas_retorno_ciudades_filter.to_excel(writer, sheet_name='Rutas retorno', index=False)
			writer.save()
			output.seek(0)

			# Define la respuesta HTTP con el contenido adecuado
			response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
			response['Content-Disposition'] = 'attachment; filename="rutas.xlsx"'

			return response
	return render(request, "ruteo/consultaRutas.html", context)