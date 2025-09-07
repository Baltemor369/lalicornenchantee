import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import base64
import time
import threading

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


# Appel de la fonction avec l'image locale
add_bg_from_local("bg.png")

geolocator = Nominatim(user_agent="equiconfort")

# Coordonnées des centres
try:
    _ = geolocator.geocode("flavigny, 57130, France")
    Centre1 = (_.latitude, _.longitude)
except:
    styled_text("Erreur lors du géocodage:")

# Titre de l'application
styled_text('Equiselle - Tarif')

# Entrée du nom de la ville
nom_ville = st.text_input("town_name","Saisir le nom de la ville ici", label_visibility="hidden")
btn = st.button("Calculer")
styled_text("Pour plus de précisions, ajoutez le code postal.</div>")
if nom_ville:
    if btn or nom_ville != "Saisir le nom de la ville ici":
        # Géocoder la ville pour obtenir ses coordonnées
        try:
            time.sleep(2)
            try:
                location = geolocator.geocode(nom_ville)
            except:
                styled_text("Error : problème lors de la localisation, actualisez la page et réessayer.")
        except Exception as e:
            styled_text("Erreur lors du géocodage:", e)
            location = None

        if location:
            coord_ville = (location.latitude, location.longitude)
            
            # Calculer les distances
            distance1 = geodesic(coord_ville, Centre1).km
            
            if nom_ville.lower() == "luxembourg":
                tarif = 75
            else:
                tarif = 0
                if distance1 <= 25:
                    tarif = 60
                elif distance1 <= 50:
                    tarif = 65
                elif distance1 <= 75:
                    tarif = 70
                elif distance1 <= 100:
                    tarif = 75
                elif distance1 <= 125:
                    tarif = 80
                elif distance1 <= 150:
                    tarif = 85
                else:
                    tarif = "À négocier"
                
            styled_text(f'<div style="background-color: rgba(255, 255, 255, 0.8);color rgb(0,0,0)">Le tarif pour {nom_ville.capitalize()} est: {tarif} €</div>')
        else:
            styled_text("Impossible de géocoder la ville.")

# Fonction qui garde l'application éveillée
def keep_awake():
    while True:
        time.sleep(60)
        print("L'application est toujours active...")

# Créer et démarrer le thread
thread = threading.Thread(target=keep_awake)
thread.daemon = True  # Permet au thread de s'arrêter lorsque l'application principale se termine
thread.start()