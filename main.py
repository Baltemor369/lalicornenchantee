import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import base64

DATE = "18/10/2026"
VERSION = "2.2.2"
BASE_PRICE = 70
OUT_PRICE = 100
# debug = True
debug = False

# Fonction pour ajouter l'image de fond locale
def add_bg_from_local(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read())
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url(data:image/jpg;base64,{encoded_string.decode()});
             background-size: cover;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
    
def styled_text(content):
    st.markdown(
        f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.7);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            color: #000000;
            font-size: 18px;
            font-family: 'Segoe UI', sans-serif;
        ">
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )

def footer_info():
    st.markdown(
        f"""
        <div style="
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: rgba(255, 255, 255, 0.6);
            padding: 8px;
            text-align: center;
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;
            color: #333;
            box-shadow: 0 -1px 5px rgba(0,0,0,0.1);
        ">
            Version : v{VERSION} | Dernière mise à jour : {DATE} | ©equiselle54
        </div>
        """,
        unsafe_allow_html=True
    )


# Appel de la fonction avec l'image locale
add_bg_from_local("bg.png")

geolocator = Nominatim(user_agent="equiconfort")

# Coordonnées des centres, géocodées une seule fois pour tout le serveur
@st.cache_resource
def get_centres():
    centre1 = geolocator.geocode("flavigny, 57130, France")
    centre2 = geolocator.geocode("hablainville, 54120, France")
    if centre1 is None or centre2 is None:
        raise ValueError("centre introuvable")
    return (centre1.latitude, centre1.longitude), (centre2.latitude, centre2.longitude)

# Géocodage des villes mis en cache pour limiter les appels à Nominatim
@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def geocode_ville(nom):
    location = geolocator.geocode(nom)
    if location is None:
        return None
    return (location.latitude, location.longitude)

# Titre de l'application
styled_text('Equiselle - Tarif')

# Entrée du nom de la ville
nom_ville = st.text_input("town_name", placeholder="Saisir le nom de la ville ici", label_visibility="hidden")
btn = st.button("Calculer")
styled_text("Pour plus de précisions, ajoutez le code postal.")
if nom_ville:
    coord_ville = None
    try:
        Centre1, Centre2 = get_centres()
        coord_ville = geocode_ville(nom_ville.strip())
        if coord_ville is None:
            styled_text("Impossible de géocoder la ville.")
    except Exception as e:
        styled_text(f"Erreur lors du géocodage, actualisez la page et réessayez. ({e})")

    if coord_ville:
        # Calculer les distances
        distance1 = geodesic(coord_ville, Centre1).km
        distance2 = geodesic(coord_ville, Centre2).km
        if debug:
            styled_text(f"dist1 = {distance1}")
            styled_text(f"dist2 = {distance2}")

        if nom_ville.strip().lower() == "luxembourg":
            tarif = 90
        else:
            tarif = 0
            if distance1 <= 25:
                tarif = BASE_PRICE
            elif distance1 <= 50:
                tarif = BASE_PRICE + 5 *1
            elif distance1 <= 75:
                tarif = BASE_PRICE + 5 *2
            elif distance1 <= 108 and distance2 <= 100:
                tarif = BASE_PRICE + 5 *3
            elif distance1 <= 145 and distance2 <= 100:
                tarif = BASE_PRICE + 5 *4
            elif distance1 <= 170 and distance2 <= 100:
                tarif = BASE_PRICE + 5 *5
            else:
                tarif = OUT_PRICE

        styled_text(f'Le tarif pour {nom_ville.strip().capitalize()} est : {tarif} €')

footer_info()