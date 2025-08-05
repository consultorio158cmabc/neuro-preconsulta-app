import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Nueva función conectar_google_sheets usando solo st.secrets (sin archivos .json locales)
def conectar_google_sheets():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    # ✅ Usa exclusivamente los secretos de Streamlit
    google_secrets = st.secrets["gcp_service_account"]
    credentials_dict = dict(google_secrets)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    return client

# Configuración de la página
st.set_page_config(page_title="Preconsulta en Neurocirugía")

# Título de la aplicación
st.title("🧠 Algoritmo de Preconsulta en Neurocirugía")

# Sección: Datos generales del paciente
st.markdown("### Datos generales del paciente")
nombre = st.text_input("Nombre completo")
edad = st.number_input("Edad", min_value=0, max_value=120)
sexo = st.selectbox("Sexo", ["Seleccione...", "Mujer", "Hombre", "Otro"])
consulta = st.radio("Tipo de consulta", ["Primera vez", "Subsecuente"])

# Validación inicial de campos generales
motivo = st.selectbox("Motivo de consulta", [
    "Seleccione...",
    "Dolor / Cirugía Lumbar",
    "Dolor / Cirugía Cervical",
    "Dolor / Cirugía Columna Dorsal",
    "Tumor Intracraneal",
    "Neuralgia del Trigémino",
    "Aneurisma Intracraneal / Malformación Arteriovenosa / Angioma Cavernoso",
    "Traumatismo Craneoencefálico",
    "Enfermedad Vascular Cerebral (EVC / Ictus)",
    "Hidrocefalia",
    "Síntomas Inespecíficos (mareo, vértigo, náusea, vómito, debilidad)",
    "Otro (especificar)"
])
campos_generales_validos = (
    nombre.strip() != "" and
    edad > 0 and
    sexo != "Seleccione..." and
    consulta in ["Primera vez", "Subsecuente"] and
    motivo != "Seleccione..."
)

# Sección: Selección de motivo de consulta
st.markdown("### Seleccione su motivo de consulta")
if motivo == "Dolor / Cirugía Lumbar":
    with st.expander("Ingresar datos de Dolor / Cirugía Lumbar", expanded=True):
        tratamiento = st.radio("Estatus de tratamiento", [
            "Seleccione...",
            "Será valorado en consulta",
            "Tratamiento con medicamentos y fisioterapia",
            "Preparación para cirugía",
            "Operado previamente con otro doctor",
            "Operado previamente con Dr. Ulises García"
        ], index=0)

        st.markdown("### Seleccione los síntomas asociados a su motivo de consulta:")
        sintomas = {
            "Dolor lumbar": st.checkbox("Dolor lumbar"),
            "Dolor con irradiación a pierna derecha": st.checkbox("Dolor con irradiación a pierna derecha"),
            "Dolor con irradiación a pierna izquierda": st.checkbox("Dolor con irradiación a pierna izquierda"),
            "Entumecimiento u hormigueo en pierna derecha": st.checkbox("Entumecimiento u hormigueo en pierna derecha"),
            "Entumecimiento u hormigueo en pierna izquierda": st.checkbox("Entumecimiento u hormigueo en pierna izquierda"),
            "Debilidad en pierna derecha": st.checkbox("Debilidad en pierna derecha"),
            "Debilidad en pierna izquierda": st.checkbox("Debilidad en pierna izquierda"),
            "Dificultad para caminar": st.checkbox("Dificultad para caminar"),
            "Incontinencia urinaria o fecal": st.checkbox("Incontinencia urinaria o fecal")
        }

        st.markdown("### Intensidad del dolor")
        st.image("VAS.jpg", caption="Escala Visual Análoga (VAS)", use_container_width=True)
        vas_lumbar = st.radio("Dolor lumbar:", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)
        vas_derecha = st.radio("Dolor en pierna derecha:", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)
        vas_izquierda = st.radio("Dolor en pierna izquierda:", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)

        st.markdown("### Funcionalidad en la vida diaria")
        st.info("En las siguientes actividades, seleccione la opción que más se parezca a su situación actual:")

        odi_preguntas = [
            ("1) Intensidad del dolor", [
                "Puedo soportar el dolor sin necesidad de tomar analgésicos",
                "El dolor es fuerte pero cede sin tomar analgésicos",
                "Los analgésicos alivian totalmente el dolor",
                "Los analgésicos alivian parcialmente el dolor",
                "Los analgésicos apenas me alivian el dolor",
                "Los analgésicos no me alivian el dolor y no los tomo"
            ]),
            ("2) Cuidado Personal", [
                "Puedo cuidar de mí mism@ de manera normal sin que esto cause dolor",
                "Puedo cuidar de mí mism@, pero esto me causa dolor",
                "Lavarme, vestirme, etc., me produce dolor y tengo que hacerlo despacio y con cuidado",
                "Necesito un poco de ayuda, pero manejo la mayoría de mi cuidado personal",
                "Necesito ayuda todos los días en la mayoría de los aspectos de mi cuidado personal",
                "No me puedo vestir, me baño con dificultad, prefiero permanecer en cama"
            ]),
            ("3) Estar de Pie", [
                "Puedo estar de pie tanto tiempo como quiera sin que aumente el dolor",
                "Puedo estar de pie tanto tiempo como quiera, pero me causa dolor",
                "El dolor me impide estar de pie más de una hora",
                "El dolor me impide estar de pie más de media hora",
                "El dolor me impide estar de pie más de 10 minutos",
                "El dolor me impide estar de pie"
            ]),
            ("4) Dormir", [
                "El dolor no me impide dormir bien",
                "Sólo puedo dormir si tomo pastillas para manejar el dolor",
                "Incluso tomando pastillas para el dolor duermo menos de 6 horas",
                "Incluso tomando pastillas para el dolor duermo menos de 4 horas",
                "Incluso tomando pastillas para el dolor duermo menos de 2 horas",
                "El dolor me impide totalmente conciliar el sueño"
            ]),
            ("5) Levantar peso", [
                "Puedo levantar objetos pesados sin que esto aumente el dolor",
                "Puedo levantar objetos pesados, pero esto aumenta el dolor",
                "El dolor me impide levantar objetos pesados del suelo, pero puedo hacerlo si están en un sitio cómodo",
                "El dolor me impide levantar objetos pesados, pero sí puedo levantar objetos ligeros o medianos si están en un sitio cómodo",
                "Sólo puedo levantar objetos muy ligeros",
                "No puedo levantar ni elevar ningún objeto"
            ]),
            ("6) Caminar", [
                "El dolor no me impide caminar",
                "El dolor me impide caminar más de 1 kilómetro",
                "El dolor me impide caminar más de 500 metros",
                "El dolor me impide caminar más de 250 metros",
                "Sólo puedo caminar con bastón o muletas",
                "Permanezco en cama casi todo el tiempo"
            ]),
            ("7) Estar sentado", [
                "Puedo estar sentado en cualquier tipo de silla todo el tiempo que quiera",
                "Puedo estar sentado en mi silla favorita todo el tiempo que quiera",
                "El dolor me impide estar sentado más de 1 hora",
                "El dolor me impide estar sentado más de media hora",
                "El dolor me impide estar sentado más de 10 minutos",
                "El dolor me impide estar sentado"
            ]),
            ("8) Vida social", [
                "Mi vida social es normal y no me aumenta el dolor",
                "Mi vida social es normal, pero aumenta el dolor",
                "El dolor no tiene un efecto importante en mi vida social, pero sí impide actividades más enérgicas",
                "El dolor limita mi vida social y no salgo tan a menudo como de costumbre",
                "El dolor limita mi vida social al hogar",
                "No tengo vida social a causa del dolor"
            ]),
            ("9) Viajar", [
                "Puedo viajar a cualquier sitio sin que aumente el dolor",
                "Puedo viajar a cualquier sitio, pero esto aumenta el dolor",
                "El dolor es fuerte, pero aguanto viajes de más de 2 horas",
                "El dolor me limita a viajes de menos de 1 hora",
                "El dolor me limita a viajes cortos y necesarios de menos de media hora",
                "El dolor me impide viajar, excepto para ir al médico o al hospital"
            ]),
            ("10) Actividad sexual", [
                "No aplica",
                "Es normal y no aumenta el dolor",
                "Es normal, pero aumenta el dolor",
                "Es casi normal, pero aumenta mucho el dolor",
                "Se ve muy limitada a causa del dolor",
                "Casi nula a causa del dolor",
                "El dolor me impide actividad sexual"
            ])
        ]

        odi_respuestas = []
        for i, (titulo, opciones) in enumerate(odi_preguntas):
            respuesta = st.radio(titulo, opciones, key=f"odi_{i}")
            if respuesta != "No aplica":
                odi_respuestas.append(opciones.index(respuesta))

        odi_total = sum(odi_respuestas)
        odi_base = 50 if len(odi_respuestas) == 10 else 45
        odi_puntaje = round((odi_total / odi_base) * 100)

        macnab = None
        if tratamiento == "Operado previamente con Dr. Ulises García":
            st.markdown("### Satisfacción del Paciente con Procedimiento Quirúrgico")
            macnab = st.radio(
                "¿Cómo describiría su estado actual tras la cirugía?",
                [
                    "Seleccione...",
                    "Excelente - No presento dolor ni restricción de la movilidad. Regresé a mi trabajo y a mis actividades cotidianas.",
                    "Bueno - Presento dolor ocasional en espalda baja, presento un alivio de los síntomas en comparación a antes de la cirugía. Regresé a mi ocupación y actividades cotidianas, pero con algunas restricciones.",
                    "Regular - Presento cierta mejoría funcional, aunque regresar al trabajo y a mis actividades cotidianas ha sido complicado.",
                    "Malo - Persisto con dolor lumbar y/o extensión hacia las piernas, requerí o estoy considerando someterme a una nueva cirugía para aliviar el dolor."
                ], index=0
            )

        campos_lumbar_validos = (
            tratamiento != "Seleccione..." and
            any(sintomas.values()) and
            vas_lumbar is not None and
            vas_derecha is not None and
            vas_izquierda is not None and
            len(odi_respuestas) >= 5 and
            (macnab is None or macnab != "Seleccione...")
        )

        if st.button("Enviar", key="enviar_lumbar"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if tratamiento == "Seleccione...":
                errores.append("Debe seleccionar el estatus de tratamiento.")
            if not any(sintomas.values()):
                errores.append("Debe seleccionar al menos un síntoma asociado.")
            if vas_lumbar is None:
                errores.append("Debe seleccionar la intensidad del dolor lumbar.")
            if vas_derecha is None:
                errores.append("Debe seleccionar la intensidad del dolor en pierna derecha.")
            if vas_izquierda is None:
                errores.append("Debe seleccionar la intensidad del dolor en pierna izquierda.")
            if len(odi_respuestas) < 5:
                errores.append("Debe responder al menos 5 preguntas de funcionalidad ODI.")
            if macnab is not None and macnab == "Seleccione...":
                errores.append("Debe seleccionar la satisfacción tras la cirugía (MacNab).")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Estatus de tratamiento": tratamiento,
                    "Síntomas": ", ".join([s for s, v in sintomas.items() if v]),
                    "VAS lumbar": vas_lumbar,
                    "VAS pierna derecha": vas_derecha,
                    "VAS pierna izquierda": vas_izquierda,
                    "ODI (%)": odi_puntaje,
                    "MacNab": macnab if macnab else "N/A"
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Dolor_Cirugía_Lumbar")
                    # Añadir encabezados si la hoja está vacía
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif motivo == "Dolor / Cirugía Cervical":
    with st.expander("Ingresar datos de Dolor / Cirugía Cervical", expanded=True):
        tratamiento_cervical = st.radio("Estatus de tratamiento", [
            "Seleccione...",
            "Será valorado en consulta",
            "Tratamiento con medicamentos y fisioterapia",
            "Preparación para cirugía",
            "Operado previamente con otro doctor",
            "Operado previamente con Dr. Ulises García"
        ], index=0)

        st.markdown("### Seleccione los síntomas asociados a su motivo de consulta:")
        sintomas_cervical = {
            "Dolor cervical": st.checkbox("Dolor cervical"),
            "Dolor con irradiación a brazo derecho": st.checkbox("Dolor con irradiación a brazo derecho"),
            "Dolor con irradiación a brazo izquierdo": st.checkbox("Dolor con irradiación a brazo izquierdo"),
            "Entumecimiento u hormigueo en brazo derecho": st.checkbox("Entumecimiento u hormigueo en brazo derecho"),
            "Entumecimiento u hormigueo en brazo izquierdo": st.checkbox("Entumecimiento u hormigueo en brazo izquierdo"),
            "Debilidad en brazo derecho": st.checkbox("Debilidad en brazo derecho"),
            "Debilidad en brazo izquierdo": st.checkbox("Debilidad en brazo izquierdo")
        }

        st.markdown("### Intensidad del dolor")
        st.image("VAS.jpg", caption="Escala Visual Análoga (VAS)", use_container_width=True)
        vas_cervical = st.radio("Dolor cervical:", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)
        vas_brazo_der = st.radio("Dolor en brazo derecho:", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)
        vas_brazo_izq = st.radio("Dolor en brazo izquierdo:", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)

        st.markdown("### Funcionalidad en la vida diaria")
        st.info("En las siguientes actividades, seleccione la opción que más se parezca a su situación actual:")

        ndi_preguntas = [
            ("1) Intensidad del dolor", [
                "No tengo dolor en este momento",
                "El dolor es tolerable en este momento",
                "El dolor es moderado en este momento",
                "El dolor es intenso en este momento",
                "El dolor es muy intenso en este momento",
                "El dolor es el peor imaginable"
            ]),
            ("2) Cuidado personal", [
                "Puedo cuidar de mí mism@ de manera normal sin que esto cause dolor",
                "Puedo cuidar de mí mism@, pero esto me causa dolor",
                "Lavarme, vestirme, etc., me produce dolor y tengo que hacerlo despacio y con cuidado",
                "Necesito un poco de ayuda, pero manejo la mayoría de mi cuidado personal",
                "Necesito ayuda todos los días en la mayoría de los aspectos de mi cuidado personal",
                "No me puedo vestir, me baño con dificultad, prefiero permanecer en cama"
            ]),
            ("3) Levantar objetos", [
                "Puedo levantar objetos pesados sin que esto cause dolor",
                "Puedo levantar objetos pesados, pero esto causa dolor",
                "El dolor me impide levantar objetos pesados del suelo, pero puedo hacerlo si están en un sitio cómodo",
                "El dolor me impide levantar objetos pesados, pero sí puedo levantar objetos ligeros o medianos si están en un sitio cómodo",
                "Sólo puedo levantar objetos muy ligeros",
                "No puedo levantar ni elevar ningún objeto"
            ]),
            ("4) Leer", [
                "Leer no me causa dolor",
                "Puedo leer todo lo que quiera con ligero dolor en mi cuello",
                "Puedo leer todo lo que quiera con dolor moderado en mi cuello",
                "No puedo leer todo lo que quiera debido a dolor moderado en mi cuello",
                "Apenas puedo leer debido al fuerte dolor en mi cuello",
                "El dolor en mi cuello no me permite leer en lo absoluto"
            ]),
            ("5) Dolor de cabeza", [
                "No tengo dolores de cabeza en lo absoluto",
                "Tengo dolores de cabeza leves, que ocurren con poca frecuencia",
                "Tengo dolores de cabeza moderados, que ocurren con poca frecuencia",
                "Tengo dolores de cabeza moderados, que ocurren con frecuencia",
                "Tengo dolores de cabeza intensos, que ocurren con frecuencia",
                "Tengo dolores de cabeza intensos casi todo el tiempo"
            ]),
            ("6) Concentración", [
                "Puedo concentrarme completamente cuando quiero, sin dificultad",
                "Puedo concentrarme completamente cuando quiero, con ligera dificultad",
                "Tengo un grado moderado de dificultad para concentrarme cuando quiero",
                "Tengo mucha dificultad para concentrarme cuando quiero",
                "Tengo demasiada dificultad para concentrarme cuando quiero",
                "No puedo concentrarme en absoluto"
            ]),
            ("7) Trabajo / Actividades Cotidianas", [
                "Puedo trabajar tanto como desee",
                "Solo puedo hacer mi trabajo habitual, pero no más",
                "Puedo hacer la mayor parte de mi trabajo habitual, pero no más",
                "No puedo hacer mi trabajo habitual",
                "Apenas puedo trabajar",
                "No puedo trabajar en absoluto"
            ]),
            ("8) Manejar", [
                "Puedo conducir mi automóvil sin ningún dolor de cuello",
                "Puedo conducir todo el tiempo que quiera, con dolor leve en el cuello",
                "Puedo conducir todo el tiempo que quiera, con dolor moderado en el cuello",
                "No puedo conducir todo el tiempo que quiera por el dolor",
                "Apenas puedo conducir por el dolor severo",
                "No puedo conducir en absoluto"
            ]),
            ("9) Dormir", [
                "No tengo problemas para dormir",
                "Mi sueño está ligeramente alterado (menos de 1 hora sin dormir)",
                "Mi sueño está levemente alterado (1–2 horas sin dormir)",
                "Mi sueño está moderadamente alterado (2–3 horas sin dormir)",
                "Mi sueño está gravemente alterado (3–5 horas sin dormir)",
                "Mi sueño está completamente alterado (5–7 horas sin dormir)"
            ]),
            ("10) Recreación", [
                "Puedo realizar todas mis actividades recreativas sin ningún dolor de cuello",
                "Puedo realizar todas mis actividades recreativas, pero con algo de dolor en el cuello",
                "Puedo realizar la mayoría, pero no todas, de mis actividades recreativas habituales",
                "Solo puedo realizar algunas de mis actividades recreativas",
                "Apenas puedo realizar actividades recreativas",
                "No puedo realizar ninguna actividad recreativa"
            ])
        ]

        ndi_respuestas = []
        for i, (titulo, opciones) in enumerate(ndi_preguntas):
            respuesta = st.radio(titulo, opciones, key=f"ndi_{i}")
            ndi_respuestas.append(opciones.index(respuesta))

        ndi_total = sum(ndi_respuestas)
        ndi_puntaje = round((ndi_total / 50) * 100)

        st.markdown("### Dificultad para la marcha")
        nurick = st.radio(
            "Seleccione el grado que mejor describa su capacidad para caminar:",
            [
                "Seleccione...",
                "0 - Sin dificultad para caminar",
                "1 - Dificultad para caminar sin limitación de la actividad",
                "2 - Dificultad para caminar que limita el rendimiento o la velocidad",
                "3 - Solo puede trabajar con asistencia de bastón o barandal",
                "4 - Requiere asistencia de otra persona",
                "5 - Confinado a silla de ruedas o cama"
            ], index=0
        )

        # --- MJOA Section ---
        st.markdown("### Sistema de Evaluación de Motricidad, Sensibilidad y Control de Esfínteres")

        mjoa_preguntas = [
            ("Función Motora de Brazos (Extremidades Superiores)", [
                "0 - Incapaz de mover las manos.",
                "1 - Incapaz de comer con una cuchara, pero capaz de mover las manos.",
                "2 - Incapacidad de abotonar una camisa, pero capaz de comer con una cuchara.",
                "3 - Capaz de abotonar una camisa con mucha dificultad.",
                "4 - Capaz de abotonar camisa con poca dificultad.",
                "5 - Sin alteraciones."
            ]),
            ("Función Motora de Piernas (Extremidades Inferiores)", [
                "0 - Pérdida completa de la movilidad y sensibilidad en piernas.",
                "1 - Preservación de la sensibilidad, incapaz de mover las piernas.",
                "2 - Capaz de mover las piernas, pero incapaz de caminar.",
                "3 - Capaz de caminar en piso plano con apoyo (ej. bastón, andadera).",
                "4 - Capaz de subir/bajar escaleras con uso de barandal.",
                "5 - Inestabilidad moderada, aunque es capaz subir/bajar escaleras sin uso de barandal.",
                "6 - Inestabilidad leve, aunque camina sin apoyo pero con marcha lenta y suave",
                "7 - Sin alteraciones"
            ]),
            ("Sensibilidad", [
                "0 - Pérdida completa de la sensibilidad en manos.",
                "1 - Pérdida severa de la sensibilidad y/o dolor.",
                "2 - Leve pérdida de la sensibilidad en manos/brazos.",
                "3 - Sin alteraciones de la sensibilidad."
            ]),
            ("Disfunción de Esfínteres", [
                "0 - Incapacidad de orinar voluntariamente.",
                "1 - Dificultad marcada para poder orinar voluntariamente.",
                "2 - Dificultad leve-moderada para orinar voluntariamente.",
                "3 - Sin alteraciones."
            ])
        ]

        mjoa_respuestas = []
        for i, (titulo, opciones) in enumerate(mjoa_preguntas):
            respuesta = st.radio(titulo, opciones, key=f"mjoa_{i}")
            mjoa_respuestas.append(opciones.index(respuesta))

        mjoa_total = sum(mjoa_respuestas)

        macnab_cervical = None
        if tratamiento_cervical == "Operado previamente con Dr. Ulises García":
            st.markdown("### Satisfacción del Paciente con Procedimiento Quirúrgico")
            macnab_cervical = st.radio(
                "¿Cómo describiría su estado actual tras la cirugía?",
                [
                    "Seleccione...",
                    "Excelente - No presento dolor ni restricción de la movilidad. Regresé a mi trabajo y a mis actividades cotidianas.",
                    "Bueno - Presento dolor ocasional en cuello o brazo, con alivio funcional comparado a antes de la cirugía.",
                    "Regular - Presento cierta mejoría funcional, pero regresar al trabajo o actividades ha sido complicado.",
                    "Malo - Persisto con dolor cervical y/o irradiación a brazos. Considero una nueva cirugía."
                ], index=0
            )

        campos_cervical_validos = (
            tratamiento_cervical != "Seleccione..." and
            any(sintomas_cervical.values()) and
            vas_cervical is not None and
            vas_brazo_der is not None and
            vas_brazo_izq is not None and
            len(ndi_respuestas) == 10 and
            nurick is not None and nurick != "Seleccione..." and
            (macnab_cervical is None or macnab_cervical != "Seleccione...")
        )

        if st.button("Enviar", key="enviar_cervical"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if tratamiento_cervical == "Seleccione...":
                errores.append("Debe seleccionar el estatus de tratamiento.")
            if not any(sintomas_cervical.values()):
                errores.append("Debe seleccionar al menos un síntoma asociado.")
            if vas_cervical is None:
                errores.append("Debe seleccionar la intensidad del dolor cervical.")
            if vas_brazo_der is None:
                errores.append("Debe seleccionar la intensidad del dolor en brazo derecho.")
            if vas_brazo_izq is None:
                errores.append("Debe seleccionar la intensidad del dolor en brazo izquierdo.")
            if len(ndi_respuestas) < 10:
                errores.append("Debe responder todas las preguntas de funcionalidad NDI.")
            if nurick is None or nurick == "Seleccione...":
                errores.append("Debe seleccionar el grado de dificultad para la marcha (Nurick).")
            if macnab_cervical is not None and macnab_cervical == "Seleccione...":
                errores.append("Debe seleccionar la satisfacción tras la cirugía (MacNab).")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seleccionados = [s for s, v in sintomas_cervical.items() if v]

                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Estatus de tratamiento": tratamiento_cervical,
                    "Síntomas": ", ".join(seleccionados),
                    "VAS cervical": vas_cervical,
                    "VAS brazo derecho": vas_brazo_der,
                    "VAS brazo izquierdo": vas_brazo_izq,
                    "NDI (%)": ndi_puntaje,
                    "Nurick": nurick,
                    "MJOA (puntos)": mjoa_total,
                    "MacNab": macnab_cervical if macnab_cervical else "N/A"
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Dolor_Cirugía_Cervical")
                    # Añadir encabezados si la hoja está vacía o no tiene valores
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif motivo == "Dolor / Cirugía Columna Dorsal":
    with st.expander("Ingresar datos de Dolor / Cirugía en columna dorsal", expanded=True):
        tratamiento_dorsal = st.radio("Estatus de tratamiento", [
            "Seleccione...",
            "Será valorado en consulta",
            "Tratamiento con medicamentos y fisioterapia",
            "Preparación para cirugía",
            "Operado previamente con otro doctor",
            "Operado previamente con Dr. Ulises García"
        ], index=0)

        st.markdown("### Seleccione los síntomas asociados a su motivo de consulta:")
        sintomas_dorsal = {
            "Dolor en columna dorsal": st.checkbox("Dolor en columna dorsal"),
            "Hormigueo o parestesias en región dorsal de la columna": st.checkbox("Hormigueo o parestesias en región dorsal de la columna")
        }

        st.markdown("### Intensidad del dolor")
        st.image("VAS.jpg", caption="Escala Visual Análoga (VAS)", use_container_width=True)
        vas_dorsal = st.radio("Dolor en columna dorsal:", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)

        st.markdown("### Dificultad para la marcha")
        nurick_dorsal = st.radio(
            "Seleccione el grado que mejor describa su capacidad para caminar:",
            [
                "Seleccione...",
                "0 - Sin dificultad para caminar",
                "1 - Dificultad para caminar sin limitación de la actividad",
                "2 - Dificultad para caminar que limita el rendimiento o la velocidad",
                "3 - Solo puede trabajar con asistencia de bastón o barandal",
                "4 - Requiere asistencia de otra persona",
                "5 - Confinado a silla de ruedas o cama"
            ], index=0
        )

        macnab_dorsal = None
        if tratamiento_dorsal == "Operado previamente con Dr. Ulises García":
            st.markdown("### Satisfacción del Paciente con Procedimiento Quirúrgico")
            macnab_dorsal = st.radio(
                "¿Cómo describiría su estado actual tras la cirugía?",
                [
                    "Seleccione...",
                    "Excelente - No presento dolor ni restricción de la movilidad. Regresé a mi trabajo y a mis actividades cotidianas.",
                    "Bueno - Presento dolor ocasional en espalda, presento un alivio de los síntomas en comparación a antes de la cirugía. Regresé a mi ocupación y actividades cotidianas, pero con algunas restricciones.",
                    "Regular - Presento cierta mejoría funcional, aunque regresar al trabajo y a mis actividades cotidianas ha sido complicado.",
                    "Malo - Persisto con dolor dorsal y/o síntomas neurológicos, requerí o estoy considerando someterme a una nueva cirugía para aliviar el dolor."
                ], index=0
            )

        campos_dorsal_validos = (
            tratamiento_dorsal != "Seleccione..." and
            any(sintomas_dorsal.values()) and
            vas_dorsal is not None and
            nurick_dorsal is not None and nurick_dorsal != "Seleccione..." and
            (macnab_dorsal is None or macnab_dorsal != "Seleccione...")
        )

        if st.button("Enviar", key="enviar_dorsal"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if tratamiento_dorsal == "Seleccione...":
                errores.append("Debe seleccionar el estatus de tratamiento.")
            if not any(sintomas_dorsal.values()):
                errores.append("Debe seleccionar al menos un síntoma asociado.")
            if vas_dorsal is None:
                errores.append("Debe seleccionar la intensidad del dolor dorsal.")
            if nurick_dorsal is None or nurick_dorsal == "Seleccione...":
                errores.append("Debe seleccionar el grado de dificultad para la marcha (Nurick).")
            if macnab_dorsal is not None and macnab_dorsal == "Seleccione...":
                errores.append("Debe seleccionar la satisfacción tras la cirugía (MacNab).")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seleccionados = [s for s, v in sintomas_dorsal.items() if v]

                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Estatus de tratamiento": tratamiento_dorsal,
                    "Síntomas": ", ".join(seleccionados),
                    "VAS dorsal": vas_dorsal,
                    "Nurick": nurick_dorsal,
                    "MacNab": macnab_dorsal if macnab_dorsal else "N/A"
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Dolor_Cirugía_Columna_Dorsal")
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif motivo == "Tumor Intracraneal":
    with st.expander("Ingresar datos de Tumor Intracraneal", expanded=True):
        tratamiento_tumor = st.radio("Estatus de tratamiento", [
            "Seleccione...",
            "Será valorado en consulta",
            "Tratamiento con medicamentos y fisioterapia",
            "Preparación para cirugía",
            "Operado previamente con otro doctor",
            "Operado previamente con Dr. Ulises García"
        ], index=0)

        st.markdown("### Seleccione los síntomas asociados a su motivo de consulta:")
        sintomas_tumor = {
            "Dolor de cabeza": st.checkbox("Dolor de cabeza"),
            "Convulsiones": st.checkbox("Convulsiones"),
            "Náusea o vómito": st.checkbox("Náusea o vómito"),
            "Cambios en la visión": st.checkbox("Cambios en la visión"),
            "Cambios en el habla": st.checkbox("Cambios en el habla"),
            "Cambios en el comportamiento": st.checkbox("Cambios en el comportamiento"),
            "Debilidad de hemicuerpo derecho": st.checkbox("Debilidad de hemicuerpo derecho"),
            "Debilidad de hemicuerpo izquierdo": st.checkbox("Debilidad de hemicuerpo izquierdo"),
            "Dificultad para comprender": st.checkbox("Dificultad para comprender"),
            "Dificultad para concentrarse": st.checkbox("Dificultad para concentrarse"),
            "Cambios en el hábito intestinal (diarrea o constipación)": st.checkbox("Cambios en el hábito intestinal (diarrea o constipación)")
        }

        st.markdown("### Estado funcional en la vida diaria")
        kps_opciones = [
            "100% - Normal; sin quejas ni evidencia de enfermedad",
            "90% - Capaz de realizar actividad normal; ligeros signos o síntomas de enfermedad",
            "80% - Actividad normal con esfuerzo; algunos signos o síntomas de enfermedad",
            "70% - Capaz de cuidarse a sí mismo; no puede realizar actividades normales",
            "60% - Requiere asistencia ocasional pero puede satisfacer la mayoría de sus necesidades personales",
            "50% - Requiere asistencia considerable y cuidados médicos frecuentes",
            "40% - Discapacitado; requiere cuidados especiales y asistencia constante",
            "30% - Severamente discapacitado; hospitalización es indicada aunque no inminente",
            "20% - Enfermo gravemente; hospitalización necesaria y tratamiento activo requerido",
            "10% - Moribundo; progresión fatal de la enfermedad"
        ]
        kps = st.radio("Seleccione la opción que más se parezca a su estado actual:", kps_opciones)

        st.markdown("### Tratamientos previos")
        radio_terapia = st.radio("¿Ha recibido radioterapia?", ["No", "Sí"])
        sesiones_radio = st.number_input("¿Cuántas sesiones ha recibido?", min_value=0, step=1) if radio_terapia == "Sí" else None

        quimio = st.radio("¿Ha recibido quimioterapia?", ["No", "Sí"])
        ciclos_quimio = st.number_input("¿Cuántos ciclos ha recibido?", min_value=0, step=1) if quimio == "Sí" else None

        campos_tumor_validos = (
            tratamiento_tumor != "Seleccione..." and
            any(sintomas_tumor.values()) and
            kps is not None and
            radio_terapia in ["No", "Sí"] and
            quimio in ["No", "Sí"] and
            (radio_terapia == "No" or sesiones_radio is not None) and
            (quimio == "No" or ciclos_quimio is not None)
        )

        if st.button("Enviar", key="enviar_tumor"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if tratamiento_tumor == "Seleccione...":
                errores.append("Debe seleccionar el estatus de tratamiento.")
            if not any(sintomas_tumor.values()):
                errores.append("Debe seleccionar al menos un síntoma asociado.")
            if kps is None:
                errores.append("Debe seleccionar el estado funcional (KPS).")
            if radio_terapia not in ["No", "Sí"]:
                errores.append("Debe indicar si ha recibido radioterapia.")
            if radio_terapia == "Sí" and sesiones_radio is None:
                errores.append("Debe indicar el número de sesiones de radioterapia.")
            if quimio not in ["No", "Sí"]:
                errores.append("Debe indicar si ha recibido quimioterapia.")
            if quimio == "Sí" and ciclos_quimio is None:
                errores.append("Debe indicar el número de ciclos de quimioterapia.")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seleccionados = [s for s, v in sintomas_tumor.items() if v]

                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Estatus de tratamiento": tratamiento_tumor,
                    "Síntomas": ", ".join(seleccionados),
                    "KPS": kps,
                    "Radioterapia": radio_terapia,
                    "Sesiones radioterapia": sesiones_radio if sesiones_radio is not None else "N/A",
                    "Quimioterapia": quimio,
                    "Ciclos quimioterapia": ciclos_quimio if ciclos_quimio is not None else "N/A"
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Tumor_Intracraneal")
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif motivo == "Neuralgia del Trigémino":
    with st.expander("Ingresar datos de Neuralgia del Trigémino", expanded=True):
        tratamiento_trigemino = st.radio("Estatus de tratamiento", [
            "Seleccione...",
            "Será valorado en consulta",
            "Tratamiento con medicamentos y fisioterapia",
            "Preparación para cirugía",
            "Operado previamente con otro doctor",
            "Operado previamente con Dr. Ulises García"
        ], index=0)

        st.markdown("### Seleccione los síntomas asociados a su motivo de consulta:")
        sintomas_trigemino = {
            "Dolor punzante en hemicara derecha": st.checkbox("Dolor punzante en hemicara derecha"),
            "Dolor punzante en hemicara izquierda": st.checkbox("Dolor punzante en hemicara izquierda"),
            "Desencadenado por estímulos como cepillarse los dientes, hablar o tocarse la cara": st.checkbox("Desencadenado por estímulos como cepillarse los dientes, hablar o tocarse la cara"),
            "Limitación funcional o ansiedad por dolor": st.checkbox("Limitación funcional o ansiedad por dolor")
        }

        st.markdown("### Intensidad del dolor")
        st.image("VAS.jpg", caption="Escala Visual Análoga (VAS)", use_container_width=True)
        vas_derecha = st.radio("Dolor en hemicara derecha:", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)
        vas_izquierda = st.radio("Dolor en hemicara izquierda:", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)

        st.markdown("### Nivel de Control del Dolor")
        bni = st.radio(
            "Seleccione la opción que más describa su situación actual:",
            [
                "Seleccione...",
                "1 - Actualmente sin dolor incluso sin tomar medicamentos",
                "2 - Dolor ocasional, no requiero de medicamentos",
                "3 - Dolor controlado adecuadamente con medicamentos",
                "4 - Dolor no controlado con medicamentos",
                "5 - Dolor severo sin alivio"
            ], index=0
        )

        campos_trigemino_validos = (
            tratamiento_trigemino != "Seleccione..." and
            any(sintomas_trigemino.values()) and
            vas_derecha is not None and
            vas_izquierda is not None and
            bni is not None and bni != "Seleccione..."
        )

        if st.button("Enviar", key="enviar_trigemino"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if tratamiento_trigemino == "Seleccione...":
                errores.append("Debe seleccionar el estatus de tratamiento.")
            if not any(sintomas_trigemino.values()):
                errores.append("Debe seleccionar al menos un síntoma asociado.")
            if vas_derecha is None:
                errores.append("Debe seleccionar la intensidad del dolor en hemicara derecha.")
            if vas_izquierda is None:
                errores.append("Debe seleccionar la intensidad del dolor en hemicara izquierda.")
            if bni is None or bni == "Seleccione...":
                errores.append("Debe seleccionar el nivel de control del dolor (BNI).")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seleccionados = [s for s, v in sintomas_trigemino.items() if v]

                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Estatus de tratamiento": tratamiento_trigemino,
                    "Síntomas": ", ".join(seleccionados),
                    "VAS hemicara derecha": vas_derecha,
                    "VAS hemicara izquierda": vas_izquierda,
                    "BNI": bni
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Neuralgia_Trigemino")
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif motivo == "Aneurisma Intracraneal / Malformación Arteriovenosa / Angioma Cavernoso":
    with st.expander("Ingresar datos de Aneurisma / MAV / Cavernoma", expanded=True):
        tratamiento_vascular = st.radio("Estatus de tratamiento", [
            "Seleccione...",
            "Será valorado en consulta",
            "Tratamiento con medicamentos y fisioterapia",
            "Preparación para cirugía",
            "Operado previamente con otro doctor",
            "Operado previamente con Dr. Ulises García"
        ], index=0)

        st.markdown("### Seleccione los síntomas asociados a su motivo de consulta:")
        sintomas_vascular = {
            "Dolor de cabeza": st.checkbox("Dolor de cabeza"),
            "Convulsiones": st.checkbox("Convulsiones"),
            "Náusea o vómito": st.checkbox("Náusea o vómito"),
            "Cambios en la visión": st.checkbox("Cambios en la visión"),
            "Cambios en el habla": st.checkbox("Cambios en el habla"),
            "Cambios en el comportamiento": st.checkbox("Cambios en el comportamiento"),
            "Debilidad de hemicuerpo derecho": st.checkbox("Debilidad de hemicuerpo derecho"),
            "Debilidad de hemicuerpo izquierdo": st.checkbox("Debilidad de hemicuerpo izquierdo"),
            "Dificultad para comprender": st.checkbox("Dificultad para comprender"),
            "Dificultad para concentrarse": st.checkbox("Dificultad para concentrarse"),
            "Cambios en el hábito intestinal (diarrea o constipación)": st.checkbox("Cambios en el hábito intestinal (diarrea o constipación)")
        }

        st.markdown("### Estado funcional en la vida diaria")
        kps_opciones = [
            "100% - Normal; sin quejas ni evidencia de enfermedad",
            "90% - Capaz de realizar actividad normal; ligeros signos o síntomas de enfermedad",
            "80% - Actividad normal con esfuerzo; algunos signos o síntomas de enfermedad",
            "70% - Capaz de cuidarse a sí mismo; no puede realizar actividades normales",
            "60% - Requiere asistencia ocasional pero puede satisfacer la mayoría de sus necesidades personales",
            "50% - Requiere asistencia considerable y cuidados médicos frecuentes",
            "40% - Discapacitado; requiere cuidados especiales y asistencia constante",
            "30% - Severamente discapacitado; hospitalización es indicada aunque no inminente",
            "20% - Enfermo gravemente; hospitalización necesaria y tratamiento activo requerido",
            "10% - Moribundo; progresión fatal de la enfermedad"
        ]
        kps_vascular = st.radio("Seleccione la opción que más se parezca a su estado actual:", kps_opciones)

        campos_vascular_validos = (
            tratamiento_vascular != "Seleccione..." and
            any(sintomas_vascular.values()) and
            kps_vascular is not None
        )

        if st.button("Enviar", key="enviar_vascular"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if tratamiento_vascular == "Seleccione...":
                errores.append("Debe seleccionar el estatus de tratamiento.")
            if not any(sintomas_vascular.values()):
                errores.append("Debe seleccionar al menos un síntoma asociado.")
            if kps_vascular is None:
                errores.append("Debe seleccionar el estado funcional (KPS).")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seleccionados = [s for s, v in sintomas_vascular.items() if v]

                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Estatus de tratamiento": tratamiento_vascular,
                    "Síntomas": ", ".join(seleccionados),
                    "KPS": kps_vascular
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Aneurisma_MAV_Cavernoma")
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif motivo == "Traumatismo Craneoencefálico":
    with st.expander("Ingresar datos de Traumatismo Craneoencefálico", expanded=True):
        st.markdown("### Nivel de Recuperación Neurológica")
        gos = st.radio(
            "Seleccione la opción que mejor describa su estado actual:",
            [
                "Seleccione...",
                "Se encuentra despierto pero no responde a su entorno (estado vegetativo)",
                "Necesita ayuda constante para todas sus actividades diarias (discapacidad severa - total)",
                "Necesita ayuda parcial para actividades diarias importantes (discapacidad severa - parcial)",
                "Es independiente en casa pero no puede trabajar ni estudiar (discapacidad moderada)",
                "Puede trabajar o estudiar con limitaciones (discapacidad moderada con adaptación)",
                "Se siente casi completamente recuperado, aunque con síntomas leves como dolor de cabeza o fatiga (buena recuperación)",
                "Se siente completamente recuperado, sin síntomas ni limitaciones (recuperación completa)"
            ], index=0
        )

        campos_tce_validos = (
            gos is not None and gos != "Seleccione..."
        )

        if st.button("Enviar", key="enviar_tce"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if gos is None or gos == "Seleccione...":
                errores.append("Debe seleccionar el estado actual (GOS-E).")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "GOS-E": gos
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Traumatismo_Craneoencefalico")
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif motivo == "Enfermedad Vascular Cerebral (EVC / Ictus)":
    with st.expander("Ingresar datos de Enfermedad Vascular Cerebral (Ictus)", expanded=True):
        tratamiento_evc = st.radio("Estatus de tratamiento", [
            "Seleccione...",
            "Será valorado en consulta",
            "Tratamiento con medicamentos y fisioterapia",
            "Preparación para cirugía",
            "Operado previamente con otro doctor",
            "Operado previamente con Dr. Ulises García"
        ], index=0)

        st.markdown("### Seleccione los síntomas asociados a su motivo de consulta:")
        sintomas_evc = {
            "Debilidad de hemicuerpo derecho": st.checkbox("Debilidad de hemicuerpo derecho"),
            "Debilidad de hemicuerpo izquierdo": st.checkbox("Debilidad de hemicuerpo izquierdo"),
            "Alteración del habla": st.checkbox("Alteración del habla"),
            "Dificultad para deglutir": st.checkbox("Dificultad para deglutir"),
            "Visión borrosa o pérdida visual parcial": st.checkbox("Visión borrosa o pérdida visual parcial"),
            "Pérdida de la conciencia": st.checkbox("Pérdida de la conciencia"),
            "Parálisis facial": st.checkbox("Parálisis facial"),
            "Alteraciones conductuales o cognitivas": st.checkbox("Alteraciones conductuales o cognitivas"),
            "Incontinencia urinaria": st.checkbox("Incontinencia urinaria"),
            "Dificultad para caminar": st.checkbox("Dificultad para caminar")
        }

        st.markdown("### Nivel de independencia funcional")
        rankin = st.radio(
            "Seleccione la opción que más se parezca a su estado actual:",
            [
                "Seleccione...",
                "0 - Sin síntomas",
                "1 - Sin discapacidad significativa; capaz de realizar todas las actividades habituales, a pesar de algunos síntomas",
                "2 - Discapacidad leve; incapaz de realizar todas las actividades previas, pero capaz de cuidar de sí mismo sin ayuda",
                "3 - Discapacidad moderada; requiere algo de ayuda, pero puede caminar sin asistencia",
                "4 - Discapacidad moderadamente severa; incapaz de atender sus propias necesidades corporales sin asistencia y no puede caminar sin ayuda",
                "5 - Discapacidad severa; confinado en cama, incontinente y requiere atención constante",
            ], index=0
        )

        campos_evc_validos = (
            tratamiento_evc != "Seleccione..." and
            any(sintomas_evc.values()) and
            rankin is not None and rankin != "Seleccione..."
        )

        if st.button("Enviar", key="enviar_evc"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if tratamiento_evc == "Seleccione...":
                errores.append("Debe seleccionar el estatus de tratamiento.")
            if not any(sintomas_evc.values()):
                errores.append("Debe seleccionar al menos un síntoma asociado.")
            if rankin is None or rankin == "Seleccione...":
                errores.append("Debe seleccionar el nivel de independencia funcional (Rankin).")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seleccionados = [s for s, v in sintomas_evc.items() if v]

                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Estatus de tratamiento": tratamiento_evc,
                    "Síntomas": ", ".join(seleccionados),
                    "mRS (Modified Rankin Scale)": rankin
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("EVC_Ictus")
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif motivo == "Hidrocefalia":
    with st.expander("Ingresar datos de Hidrocefalia", expanded=True):
        tratamiento_hidro = st.radio("Estatus de tratamiento", [
            "Seleccione...",
            "Será valorado en consulta",
            "Tratamiento con medicamentos y fisioterapia",
            "Preparación para cirugía",
            "Operado previamente con otro doctor",
            "Operado previamente con Dr. Ulises García"
        ], index=0)

        st.markdown("### Seleccione los síntomas asociados a su motivo de consulta:")
        sintomas_hidro = {
            "Dificultad para caminar": st.checkbox("Dificultad para caminar"),
            "Incontinencia urinaria": st.checkbox("Incontinencia urinaria"),
            "Alteraciones en la memoria o lentitud cognitiva": st.checkbox("Alteraciones en la memoria o lentitud cognitiva"),
            "Inestabilidad al estar de pie": st.checkbox("Inestabilidad al estar de pie"),
            "Arrastre de pies o pasos cortos": st.checkbox("Arrastre de pies o pasos cortos"),
            "Caídas frecuentes": st.checkbox("Caídas frecuentes"),
            "Urgencia para orinar": st.checkbox("Urgencia para orinar"),
            "Alteración en el juicio o apatía": st.checkbox("Alteración en el juicio o apatía"),
            "Dificultad para iniciar la marcha": st.checkbox("Dificultad para iniciar la marcha")
        }

        campos_hidro_validos = (
            tratamiento_hidro != "Seleccione..." and
            any(sintomas_hidro.values())
        )

        if st.button("Enviar", key="enviar_hidro"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if tratamiento_hidro == "Seleccione...":
                errores.append("Debe seleccionar el estatus de tratamiento.")
            if not any(sintomas_hidro.values()):
                errores.append("Debe seleccionar al menos un síntoma asociado.")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seleccionados = [s for s, v in sintomas_hidro.items() if v]

                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Estatus de tratamiento": tratamiento_hidro,
                    "Síntomas": ", ".join(seleccionados)
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Hidrocefalia")
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")

elif motivo == "Síntomas Inespecíficos (mareo, vértigo, náusea, vómito, debilidad)":
    with st.expander("Ingresar datos de Síntomas Inespecíficos", expanded=True):
        tratamiento_inesp = st.radio("Estatus de tratamiento", [
            "Seleccione...",
            "Será valorado en consulta",
            "Tratamiento con medicamentos y fisioterapia",
            "Preparación para cirugía",
            "Operado previamente con otro doctor",
            "Operado previamente con Dr. Ulises García"
        ], index=0)

        st.markdown("### Seleccione los síntomas asociados a su motivo de consulta:")
        sintomas_inesp = {
            "Mareo": st.checkbox("Mareo"),
            "Vértigo": st.checkbox("Vértigo"),
            "Náusea": st.checkbox("Náusea"),
            "Vómito": st.checkbox("Vómito"),
            "Debilidad general": st.checkbox("Debilidad general"),
            "Sensación de desmayo": st.checkbox("Sensación de desmayo"),
            "Zumbido en los oídos (acúfenos)": st.checkbox("Zumbido en los oídos (acúfenos)"),
            "Visión borrosa o doble": st.checkbox("Visión borrosa o doble"),
            "Inestabilidad al caminar": st.checkbox("Inestabilidad al caminar"),
            "Cefalea leve": st.checkbox("Cefalea leve"),
            "Alteración del equilibrio": st.checkbox("Alteración del equilibrio"),
            "Intolerancia al movimiento": st.checkbox("Intolerancia al movimiento")
        }

        st.markdown("### Intensidad de los síntomas")
        st.image("VAS.jpg", caption="Escala Visual Análoga (VAS)", use_container_width=True)
        vas_inesp = st.radio("¿Qué tan intensos son sus síntomas actualmente?", [f"{i}%" for i in range(0, 101, 10)], horizontal=True)

        campos_inesp_validos = (
            tratamiento_inesp != "Seleccione..." and
            any(sintomas_inesp.values()) and
            vas_inesp is not None
        )

        if st.button("Enviar", key="enviar_inesp"):
            errores = []
            if not campos_generales_validos:
                if nombre.strip() == "":
                    errores.append("Debe ingresar el nombre completo.")
                if edad <= 0:
                    errores.append("Debe ingresar una edad válida.")
                if sexo == "Seleccione...":
                    errores.append("Debe seleccionar el sexo.")
                if consulta not in ["Primera vez", "Subsecuente"]:
                    errores.append("Debe seleccionar el tipo de consulta.")
                if motivo == "Seleccione...":
                    errores.append("Debe seleccionar el motivo de consulta.")
            if tratamiento_inesp == "Seleccione...":
                errores.append("Debe seleccionar el estatus de tratamiento.")
            if not any(sintomas_inesp.values()):
                errores.append("Debe seleccionar al menos un síntoma asociado.")
            if vas_inesp is None:
                errores.append("Debe seleccionar la intensidad de los síntomas.")
            if errores:
                st.error("❌ Por favor complete los siguientes campos obligatorios antes de enviar el formulario:\n\n" + "\n".join([f"- {e}" for e in errores]))
            else:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seleccionados = [s for s, v in sintomas_inesp.items() if v]

                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Estatus de tratamiento": tratamiento_inesp,
                    "Síntomas": ", ".join(seleccionados),
                    "VAS general": vas_inesp
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Sintomas_Inespecificos")
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif motivo == "Otro (especificar)":
    with st.expander("Ingresar datos de Otro motivo de consulta", expanded=True):
        motivo_otro = st.text_input("Describa brevemente el motivo de su consulta:")
        sintomas_otro = st.text_area("Describa los síntomas que presenta:")

        campos_otro_validos = (
            motivo_otro.strip() != "" and sintomas_otro.strip() != ""
        )

        if st.button("Enviar", key="enviar_otro"):
            if campos_generales_validos and campos_otro_validos:
                st.success("✅ Agradecemos por su visita, en breve lo pasamos a su consulta")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                datos = {
                    "Fecha y hora": timestamp,
                    "Nombre": nombre,
                    "Edad": edad,
                    "Sexo": sexo,
                    "Tipo de consulta": consulta,
                    "Motivo especificado": motivo_otro,
                    "Síntomas": sintomas_otro
                }

                df = pd.DataFrame([datos])
                try:
                    client = conectar_google_sheets()
                    sheet = client.open("respuestas_neuro").worksheet("Otro")
                    if sheet.row_count == 0 or not any(sheet.row_values(1)):
                        sheet.append_row(list(datos.keys()))
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")
            else:
                st.error("❌ Por favor complete todos los campos obligatorios antes de enviar el formulario.")
elif motivo != "Seleccione..." and motivo not in [
    "Dolor / Cirugía Lumbar",
    "Dolor / Cirugía Cervical",
    "Dolor / Cirugía Columna Dorsal"
    "Tumor Intracraneal",
    "Neuralgia del Trigémino",
    "Aneurisma Intracraneal / Malformación Arteriovenosa / Angioma Cavernoso",
    "Traumatismo Craneoencefálico"
    "Enfermedad Vascular Cerebral (EVC / Ictus)",
    "Hidrocefalia"
    "Síntomas Inespecíficos (mareo, vértigo, náusea, vómito, debilidad)"
    "Otro (especificar)"
]:
    st.warning("⚠️ Esta sección estará disponible próximamente.")