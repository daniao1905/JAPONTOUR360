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
    "Medio tour Tokyo": 0,
    "Medio tour Osaka": 0,
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

st.markdown("Selecciona un rango de fechas para el servicio:")
fecha_inicio = st.date_input("Desde", date.today())
fecha_fin = st.date_input("Hasta", date.today() + timedelta(days=1))

pdf_data = []
total_general = 0

if fecha_inicio <= fecha_fin and cliente:
    fechas = [fecha_inicio + timedelta(days=i) for i in range((fecha_fin - fecha_inicio).days + 1)]

    for fecha in fechas:
        st.markdown(f"---\n### {fecha.strftime('%A, %d %B %Y')}")

        servicio = st.selectbox(
            f"Servicio principal para {fecha}",
            ["Seleccione servicio"] + list(precios.keys()),
            key=f"servicio_{fecha},
            label_visibility='visible'
        )

        personas = st.number_input(f"Número de personas ({fecha})", 1, 30, key=f"personas_{fecha}")
        traslado_aeropuerto = st.checkbox(f"Incluir Traslado Aeropuerto - Hotel para {fecha} (+¥56,000)", key=f"aeropuerto_{fecha}")
        traslado_estacion = st.checkbox(f"Incluir Traslado Estación - Hotel para {fecha} (+¥49,000)", key=f"estacion_{fecha}")
        vehiculo = st.selectbox(f"Vehículo requerido ({fecha})", list(vehiculos_tarifa.keys()), key=f"vehiculo_{fecha}")

        # Calcular base dinámicamente
        if servicio.startswith("Medio tour"):
            tour_equivalente = "Tour " + servicio.split(" ")[-1]
            base = int(precios.get(tour_equivalente, 0) * 0.5)
        else:
            base = precios.get(servicio, 0)

        if servicio != "Seleccione servicio":
            st.caption(f"Tarifa base (1–5 pax): ¥{base:,}")

        extra = (personas - 5) * 10000 if personas > 5 else 0
        traslado_cost = 56000 if traslado_aeropuerto else 0
        traslado_cost += 49000 if traslado_estacion else 0
        vehiculo_costo = vehiculos_tarifa[vehiculo]
        total = base + extra + traslado_cost + vehiculo_costo
        total_general += total

        pdf_data.append({
            "fecha": fecha.strftime("%d/%m/%Y"),
            "servicio": servicio if servicio != "Seleccione servicio" else "No definido",
            "personas": personas,
            "vehiculo": vehiculo,
            "traslado_cost": traslado_cost,
            "base": base,
            "extra": extra,
            "vehiculo_costo": vehiculo_costo,
            "total": total
        })

    st.markdown("---")
    st.markdown(f"### Total por todas las fechas: ¥{total_general:,}")

    if st.button("Generar factura PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, f"Factura - Cliente: {cliente}", ln=True, align="L")
        pdf.ln(5)

        for item in pdf_data:
            pdf.set_font("Arial", 'B', size=12)
            pdf.cell(0, 10, f"{item['fecha']} - {item['servicio']}", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 8, f"Personas: {item['personas']}", ln=True)
            pdf.cell(0, 8, f"Vehículo: {item['vehiculo']} (¥{item['vehiculo_costo']:,})", ln=True)
            pdf.cell(0, 8, f"Traslados incluidos: ¥{item['traslado_cost']:,}", ln=True)
            pdf.cell(0, 8, f"Base: ¥{item['base']:,} | Extra pax: ¥{item['extra']:,}", ln=True)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 8, f"Total Día: ¥{item['total']:,}", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)

        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 10, f"Total General: ¥{total_general:,}", ln=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            st.success("Factura generada correctamente.")
            with open(tmp.name, "rb") as f:
                st.download_button("Descargar PDF", data=f.read(), file_name=f"factura_{cliente}.pdf")
