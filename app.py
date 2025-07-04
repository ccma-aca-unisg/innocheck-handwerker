import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Deckungsbeitragsrechnung", layout="wide")

st.title("Deckungsbeitragsrechnung – Handwerkerauftrag")

st.sidebar.header("Eingabewerte")

# Einnahmen
umsatz = st.sidebar.number_input("Umsatz (CHF)", min_value=0.0, value=100000.0, step=1000.0)

# Variable Kosten
st.sidebar.subheader("Variable Kosten")
materialkosten = st.sidebar.number_input("Materialkosten (CHF)", min_value=0.0, value=25000.0)
arbeitsstunden = st.sidebar.number_input("Arbeitsstunden", min_value=0.0, value=160.0)
stundensatz = st.sidebar.number_input("Stundensatz (CHF)", min_value=0.0, value=45.0)
entfernung = st.sidebar.number_input("Entfernung (km)", min_value=0.0, value=50.0)
benzinpreis = st.sidebar.number_input("Benzinpreis pro km (CHF)", min_value=0.0, value=0.35)
fahrten = st.sidebar.number_input("Anzahl der Fahrten", min_value=0.0, value=20.0)

# Fixkosten
st.sidebar.subheader("Fixkosten")
opportunitaetskosten = st.sidebar.number_input("Opportunitätskosten pro Tag (CHF)", min_value=0.0, value=200.0)
projekttage = st.sidebar.number_input("Projektdauer (Tage)", min_value=0.0, value=20.0)
verwaltung = st.sidebar.number_input("Verwaltungskosten (CHF)", min_value=0.0, value=2000.0)
versicherung = st.sidebar.number_input("Versicherungskosten (CHF)", min_value=0.0, value=1500.0)

# === Berechnungen ===

arbeitskosten = arbeitsstunden * stundensatz
transportkosten = entfernung * benzinpreis * fahrten

variable_kosten = {
    "Materialkosten": materialkosten,
    "Arbeitskosten": arbeitskosten,
    "Transportkosten": transportkosten
}

fixkosten = {
    "Opportunitätskosten": opportunitaetskosten * projekttage,
    "Verwaltungskosten": verwaltung,
    "Versicherungskosten": versicherung
}

summe_vk = sum(variable_kosten.values())
deckungsbeitrag = umsatz - summe_vk
summe_fk = sum(fixkosten.values())
betriebsergebnis = deckungsbeitrag - summe_fk

# === Ergebnisanzeige ===
st.header("Ergebnis")
st.write(f"**Umsatz:** {umsatz:,.2f} CHF".replace(",", "'"))
st.write(f"**Variable Kosten:** {summe_vk:,.2f} CHF".replace(",", "'"))
st.write(f"**Deckungsbeitrag:** {deckungsbeitrag:,.2f} CHF".replace(",", "'"))
st.write(f"**Fixkosten:** {summe_fk:,.2f} CHF".replace(",", "'"))
st.write(f"**Betriebsergebnis:** {betriebsergebnis:,.2f} CHF".replace(",", "'"))

# === Wasserfall-Diagramm ===
st.subheader("Wasserfalldiagramm (Deckungsbeitragsrechnung)")

# Step-wise calculation
deckungsbeitrag = umsatz - summe_vk
betriebsergebnis = deckungsbeitrag - summe_fk

# Prepare waterfall steps with defined logic
steps = [
    {"Kategorie": "Umsatz", "Wert": umsatz, "bottom": 0},
    {"Kategorie": "Variable Kosten", "Wert": -summe_vk},  # relative to previous
    {"Kategorie": "Deckungsbeitrag", "Wert": deckungsbeitrag},  # absolute value
    {"Kategorie": "Fixkosten", "Wert": -summe_fk},  # relative to previous
    {"Kategorie": "Betriebsergebnis", "Wert": betriebsergebnis, "bottom": 0}  # always start from 0
]

# Compute waterfall positions
bars = []
running_total = 0

for step in steps:
    value = step["Wert"]
    label = step["Kategorie"]
    
    if "bottom" in step:
        bottom = step["bottom"]  # force it (like 0 for Umsatz and Ergebnis)
    else:
        bottom = running_total if value < 0 else 0  # negative values stacked down
    
    top = bottom + value
    bars.append({
        "Kategorie": label,
        "Betrag": value,
        "Start": bottom,
        "Ende": top
    })

    # update total only for flow values, not for "absolute" result
    if label not in ["Deckungsbeitrag", "Betriebsergebnis"]:
        running_total += value

# Create DataFrame
df = pd.DataFrame(bars)

# Set colors
colors = {
    "Umsatz": "#3498db",
    "Variable Kosten": "#e74c3c",
    "Deckungsbeitrag": "#2ecc71",
    "Fixkosten": "#f39c12",
    "Betriebsergebnis": "#27ae60" if betriebsergebnis >= 0 else "#c0392b"
}

# Plot
fig, ax = plt.subplots(figsize=(10, 5))

for i, row in df.iterrows():
    bar_color = colors[row["Kategorie"]]
    height = row["Ende"] - row["Start"]
    ax.bar(row["Kategorie"], height, bottom=row["Start"], color=bar_color)
    
    # Place label correctly
    offset = umsatz * 0.01
    va = "bottom" if height >= 0 else "top"
    ax.text(i, row["Ende"] + (offset if height >= 0 else -offset),
            f"{row['Betrag']:,.0f}".replace(",", "'"), ha="center", va=va)

# Axes
ax.axhline(0, color='black', linewidth=0.8)
ax.set_ylabel("CHF")
ax.set_title("Deckungsbeitragsrechnung")
plt.xticks(rotation=45)
st.pyplot(fig)

# === Kostenaufstellung ===
st.subheader("Kostenaufstellung")

kostenliste = {**variable_kosten, **fixkosten}
df_kosten = pd.DataFrame(list(kostenliste.items()), columns=["Kostenkategorie", "Betrag in CHF"])
df_kosten["Typ"] = ["Variable Kosten"] * len(variable_kosten) + ["Fixkosten"] * len(fixkosten)
df_kosten = df_kosten[["Kostenkategorie", "Typ", "Betrag in CHF"]]
df_kosten["Betrag in CHF"] = df_kosten["Betrag in CHF"].map(lambda x: f"{x:,.2f}".replace(",", "'"))

st.table(df_kosten)
