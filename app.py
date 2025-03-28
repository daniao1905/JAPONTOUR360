import streamlit as st
from datetime import date, timedelta
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Presupuesto Japon Tour 360", layout="centered")
st.title("Presupuesto JAPÓN TOUR 360")

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

vehiculo_tarifa = {
    "Ninguno": 0,
    "Alphard": 61500,
    "Hiace": 67500
}

fecha_inicio = st.date_input("Desde", date.today())
fecha_fin = st.date_input("Hasta", date.today())

pdf_data = []
total_general = 0

if fecha_inicio <= fecha_fin and cliente:
    fechas = [fecha_inicio + timedelta(days=i) for i in range((fecha_fin - fecha_inicio).days + 1)]

    for fecha in fechas:
        st.markdown(f"---\n### {fecha.strftime('%A, %d %B %Y')}")

        servicio = st.selectbox(
            f"Servicio para {fecha}",
            ["Seleccione servicio"] + list(precios.keys()),
            key=f"servicio_{fecha}"
        )

        personas = st.number_input(f"Número de personas ({fecha})", 1, 30, key=f"personas_{fecha}")
        vehiculo = st.selectbox(f"¿Vehículo requerido? ({fecha})", list(vehiculo_tarifa.keys()), key=f"vehiculo_{fecha}")

        traslado_aeropuerto = st.checkbox(f"Incluir traslado Aeropuerto-Hotel (+¥56,000)", key=f"traslado_air_{fecha}")
        traslado_estacion = st.checkbox(f"Incluir traslado Estación-Hotel (+¥49,000)", key=f"traslado_sta_{fecha}")

        if servicio.startswith("Medio tour"):
            tour_equivalente = "Tour " + servicio.split(" ")[-1]
            base = int(precios.get(tour_equivalente, 0) * 0.5)
        else:
            base = precios.get(servicio, 0)

        extra = (personas - 5) * 10000 if personas > 5 else 0
        traslado_cost = 0
        if traslado_aeropuerto:
            traslado_cost += 56000
        if traslado_estacion:
            traslado_cost += 49000

        vehiculo_costo = vehiculo_tarifa[vehiculo]
        total = base + extra + vehiculo_costo + traslado_cost
        total_general += total

        pdf_data.append({
            "fecha": fecha.strftime("%d/%m/%Y"),
            "servicio": servicio,
            "personas": personas,
            "vehiculo": vehiculo,
            "traslado_cost": traslado_cost,
            "base": base,
            "extra": extra,
            "vehiculo_costo": vehiculo_costo,
            "total": total
        })

    st.markdown("---")
    st.markdown(f"### Total: ¥{total_general:,}")

    if st.button("Generar presupuesto PDF"):
        class PDF(FPDF):
            def header(self):
                self.image("logo.png", 10, 8, 30)
                self.set_xy(50, 10)
                self.set_font("Arial", 'B', 14)
                self.cell(0, 10, "Presupuesto - JAPÓN TOUR 360", ln=True)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.ln(25)
        pdf.set_xy(10, 40)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Cliente: {cliente}", ln=True)

        pdf.ln(4)
        for item in pdf_data:
            pdf.set_font("Arial", 'B', size=12)
            pdf.cell(0, 10, f"{item['fecha']} - {item['servicio']}", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.cell(0, 8, f"Personas: {item['personas']}", ln=True)
            pdf.cell(0, 8, f"Vehículo: {item['vehiculo']} (¥{item['vehiculo_costo']:,})", ln=True)
            pdf.cell(0, 8, f"Traslados: ¥{item['traslado_cost']:,}", ln=True)
            pdf.cell(0, 8, f"Base: ¥{item['base']:,} | Extra pax: ¥{item['extra']:,}", ln=True)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 8, f"Total Día: ¥{item['total']:,}", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)

        pdf.set_font("Arial", 'B', size=13)
        pdf.cell(0, 10, f"Total General: ¥{total_general:,}", ln=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            st.success("Presupuesto generado correctamente.")
            with open(tmp.name, "rb") as f:
                st.download_button("Descargar PDF", data=f.read(), file_name=f"presupuesto_{cliente}.pdf")
