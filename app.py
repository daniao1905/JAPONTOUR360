import streamlit as st
from datetime import date, timedelta
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Servicios VIP PDF", layout="centered")
st.title("Reserva de Servicios Turísticos VIP")

cliente = st.text_input("Nombre del cliente")

precios = {
    "Traslado Aeropuerto - Hotel": 56000,
    "Traslado Estacionamiento - Hotel": 49000,
    "Medio tour Tokyo": 49000,
    "Medio tour Osaka": 49000,
    "Tour Tokyo": 59000,
    "Tour Osaka": 69000,
    "Tour Kyoto": 69000,
    "Tour Nara": 69000,
    "Tour Kobe": 69000,
    "Tour Hiroshima": 69000,
    "Tour Fukuoka": 69000,
    "Tour Nikko Ruta 1": 79000,
    "Tour Nikko Ruta 2": 89000,
    "Tour Hakone": 69000
}

vehiculos_tarifa = {
    "Ninguno": 0,
    "Alphard": 61500,
    "Hiace": 67500
}

adicionales = {
    "Ninguno": 0,
    "Traslado Aeropuerto - Hotel": 56000,
    "Traslado Estacionamiento - Hotel": 49000
}

st.markdown("Selecciona un rango de fechas para el servicio:")
fecha_inicio = st.date_input("Desde", date.today())
fecha_fin = st.date_input("Hasta", date.today() + timedelta(days=1))

pdf_data = []
total_general = 0

if fecha_inicio <= fecha_fin and cliente:
    fechas = [fecha_inicio + timedelta(days=i) for i in range((fecha_fin - fecha_inicio).days + 1)]

    for fecha in fechas:
        st.markdown(f"---\n### {fecha.strftime('%A, %d %B %Y')}")

        servicio = st.selectbox(f"Servicio principal para {fecha}", list(precios.keys()), key=f"servicio_{fecha}")
        st.caption(f"Tarifa base (1–5 pax): ¥{precios[servicio]:,}")

        personas = st.number_input(f"Número de personas ({fecha})", 1, 30, key=f"personas_{fecha}")
        horas = st.number_input(f"Horas de servicio ({fecha})", 1, 12, key=f"horas_{fecha}")

        adicional = st.selectbox(f"¿Servicio adicional ({fecha})?", list(adicionales.keys()), key=f"adicional_{fecha}")
        if adicional != "Ninguno":
            st.caption(f"Tarifa adicional: ¥{adicionales[adicional]:,}")

        vehiculo = st.selectbox(f"Vehículo requerido ({fecha})", list(vehiculos_tarifa.keys()), key=f"vehiculo_{fecha}")
        if vehiculo != "Ninguno":
            st.caption(f"Tarifa vehículo ({vehiculo}): ¥{vehiculos_tarifa[vehiculo]:,}")

        base = precios[servicio]
        extra = (personas - 5) * 10000 if personas > 5 else 0
        adicional_costo = adicionales[adicional]
        vehiculo_costo = vehiculos_tarifa[vehiculo]

        total = base + extra + adicional_costo + vehiculo_costo
        total_general += total

        pdf_data.append({
            "fecha": fecha.strftime("%d/%m/%Y"),
            "servicio": servicio,
            "personas": personas,
            "horas": horas,
            "vehiculo": vehiculo,
            "adicional": adicional,
            "base": base,
            "extra": extra,
            "adicional_costo": adicional_costo,
            "vehiculo_costo": vehiculo_costo,
            "total": total
        })

    st.markdown("---")
    st.markdown(f"### Total por todas las fechas: ¥{total_general:,}")

    if st.button("Generar factura PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Factura - Cliente: {cliente}", ln=True, align="L")
        pdf.ln(5)

        for item in pdf_data:
            pdf.multi_cell(0, 8,
                f"{item['fecha']} - {item['servicio']}\n"
                f"Personas: {item['personas']} | Horas: {item['horas']}\n"
                f"Adicional: {item['adicional']} (¥{item['adicional_costo']:,})\n"
                f"Vehículo: {item['vehiculo']} (¥{item['vehiculo_costo']:,})\n"
                f"Base: ¥{item['base']:,} | Extra pax: ¥{item['extra']:,} | Total Día: ¥{item['total']:,}\n", border=0)
            pdf.ln(2)

        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 10, f"Total General: ¥{total_general:,}", ln=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            st.success("Factura generada correctamente.")
            with open(tmp.name, "rb") as f:
                st.download_button("Descargar PDF", data=f.read(), file_name=f"factura_{cliente}.pdf")
