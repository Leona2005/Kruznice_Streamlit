import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# Nastavení stránky
st.set_page_config(
    page_title="Generátor Bodů na Kružnici",
    layout="wide"
)

# --- KONSTANTY A FUNKCE ---

def vypocet_bodu(x0, y0, r, n):
    """Vypočítá souřadnice N bodů na kružnici."""
    # Vytvoří N rovnoměrně rozdělených úhlů od 0 do 2*pi
    uhly = np.linspace(0, 2 * np.pi, n, endpoint=False)
    
    # Parametrické rovnice kružnice
    x = x0 + r * np.cos(uhly)
    y = y0 + r * np.sin(uhly)
    
    return x, y

def vytvor_graf(x, y, x0, y0, r, barva, jednotka):
    """Vykreslí kružnici, body a osy s jednotkami."""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Vykreslení bodů
    ax.scatter(x, y, color=barva, label=f'{len(x)} bodů')
    
    # Vykreslení středu
    ax.scatter([x0], [y0], color='red', marker='x', s=100, label='Střed')
    
    # Nastavení os
    ax.set_xlabel(f'X osa [{jednotka}]')
    ax.set_ylabel(f'Y osa [{jednotka}]')
    ax.set_title(f'Kružnice (Poloměr = {r} {jednotka})')
    
    # Zajistíme, aby osy měly stejné měřítko (kružnice vypadá jako kruh)
    ax.set_aspect('equal', adjustable='box')
    
    # Vykreslení samotné kružnice pro kontext
    kruh = plt.Circle((x0, y0), r, color='gray', fill=False, linestyle='--')
    ax.add_artist(kruh)
    
    ax.grid(True)
    ax.legend()
    
    return fig

def generuj_pdf(x, y, parametry, jmeno_kontakt, plot_buffer):
    """Vygeneruje PDF soubor s výsledky a informacemi."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Nadpis
    pdf.cell(0, 10, "Zpráva - Body na Kružnici", 0, 1, "C")
    
    # Parametry
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Vstupní Parametry:", 0, 1)
    pdf.set_font("Arial", "", 10)
    for key, value in parametry.items():
        pdf.cell(0, 5, f"- {key}: {value}", 0, 1)
        
    # Informace o autorovi
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Informace o Tvůrci:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, jmeno_kontakt)

    # Graf
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3. Vykreslený Graf:", 0, 1)
    pdf.image(plot_buffer, x=10, y=pdf.get_y(), w=180) 
    
    # Tabulka souřadnic (volitelné, zjednodušeno pro PDF)
    pdf.set_y(pdf.get_y() + 120) # Posun dolů pod obrázek
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "4. Prvních 5 Bodů (X, Y):", 0, 1)
    pdf.set_font("Arial", "", 10)
    for i in range(min(5, len(x))):
        pdf.cell(0, 5, f"Bod {i+1}: ({x[i]:.3f}, {y[i]:.3f})", 0, 1)

    return pdf.output(dest='S').encode('latin1')


# --- APLIKACE V RÁMCI STREAMLIT ---

st.title("Generátor Bodů na Kružnici 🌐")

# 1. Postranní panel pro Informace o vás
with st.sidebar:
    st.header("Informace o projektu")
    st.subheader("Autor a Kontakt")
    st.write("Jméno: Váš Případný Kontakt (např. Jan Novák)")
    st.write("E-mail: vas@email.cz")
    st.write("Kontakt/Web: Váš GitHub/LinkedIn (volitelné)")
    st.markdown("---")
    st.subheader("Použité Technologie")
    st.markdown("""
    - **Python**
    - **Streamlit** (webové rozhraní)
    - **NumPy** (matematické výpočty)
    - **Matplotlib** (vizualizace)
    - **Fpdf2** (generování PDF)
    """)
    jmeno_kontakt = "Jméno: Leona Bednáříková\nE-mail: 277665@vutbr.cz\nGitHub: https://github.com/vas-profil (Doporučeno)"


# 2. Vstupní parametry
col1, col2, col3 = st.columns(3)

x0 = col1.number_input("Střed X (x₀)", value=0.0)
y0 = col2.number_input("Střed Y (y₀)", value=0.0)
jednotka = col3.selectbox("Jednotka", ["m", "cm", "km", "jednotka"])

r = st.slider("Poloměr (r)", min_value=1.0, max_value=100.0, value=50.0, step=0.1)
n = st.number_input("Počet bodů (n)", min_value=3, max_value=500, value=12, step=1)
barva = st.color_picker("Barva bodů", value='#FF4B4B')

# Kontrola poloměru
if r <= 0:
    st.error("Poloměr musí být kladné číslo.")
else:
    # 3. Výpočet
    x, y = vypocet_bodu(x0, y0, r, n)
    
    # 4. Vykreslení grafu
    fig = vytvor_graf(x, y, x0, y0, r, barva, jednotka)
    st.pyplot(fig) # Zobrazíme graf ve Streamlitu

    # Tisk prvních 5 souřadnic pod graf
    st.subheader("Souřadnice prvních 5 bodů")
    data = {'X souřadnice': x[:5], 'Y souřadnice': y[:5]}
    st.dataframe(data, hide_index=True)


    # 5. Tisk do PDF
    parametry = {
        "Střed": f"({x0}, {y0})",
        "Poloměr (r)": f"{r} {jednotka}",
        "Počet bodů (n)": n,
        "Barva bodů": barva
    }
    
    # Uložení grafu do bufferu (paměti) pro PDF
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches="tight")
    buf.seek(0)
    
    # Generování a stažení PDF
    pdf_output = generuj_pdf(x, y, parametry, jmeno_kontakt, buf)
    
    st.download_button(
        label="Stáhnout Zprávu jako PDF 📄",
        data=pdf_output,
        file_name="Zprava_Kruznice.pdf",
        mime="application/pdf"
    )
