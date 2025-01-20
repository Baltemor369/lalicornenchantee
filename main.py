import streamlit as st
from const import *

# Titre de l'application
st.title('Tarifs des Villes')

# Affichage du listing des villes et tarifs
# st.subheader('Liste des villes et leurs tarifs')
# for ville, tarif in villes_tarifs.items():
#     st.write(f"{ville}: {tarif} €")

# Entrée du nom de la ville
nom_ville = st.text_input("Entrez le nom de la ville pour obtenir le tarif:")

# Récupération et affichage du tarif correspondant
if nom_ville:
    tarif = villes_tarifs.get(nom_ville, "Ville non trouvée")
    st.write(f"Le tarif pour {nom_ville} est: {tarif} €")
