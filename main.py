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

# Appel de la fonction avec l'image locale
add_bg_from_local("bg.png")

geolocator = Nominatim(user_agent="equiconfort")

# Coordonnées des centres
try:
    _ = geolocator.geocode("flavigny, 57130, France")
    Centre1 = (_.latitude, _.longitude)

    _ = geolocator.geocode("hablainville, 54120, France")
    Centre2 = (_.latitude, _.longitude)
except:
    st.write("Erreur lors du géocodage:")

# Titre de l'application
st.title('Equiselle - Tarif')

# Entrée du nom de la ville
nom_ville = st.text_input("Entrez le nom de la ville pour obtenir le tarif:")
st.markdown("<div style='background-color: rgba(255, 255, 255, 0.8);'>Pour plus de précisions, ajoutez le code postal.</div>", unsafe_allow_html=True)

if nom_ville:
    # Géocoder la ville pour obtenir ses coordonnées
    try:
        time.sleep(2)
        try:
            location = geolocator.geocode(nom_ville)
        except:
            st.write("Error : problème lors de la localisation, actualisez la page et réessayer.")
    except Exception as e:
        st.write("Erreur lors du géocodage:", e)
        location = None

    if location:
        coord_ville = (location.latitude, location.longitude)
        
        # Calculer les distances
        distance1 = geodesic(coord_ville, Centre1).km
        distance2 = geodesic(coord_ville, Centre2).km
        
        if nom_ville.lower() == "luxembourg":
            tarif = 75
        else:
            tarif = 0
            if distance1 <= 25 or distance2 <= 25:
                tarif = 60
            elif distance1 <= 50 or distance2 <= 50:
                tarif = 65
            elif distance1 <= 75 or distance2 <= 75:
                tarif = 70
            elif distance2 <= 110:
                tarif = 75
            else:
                tarif = "À négocier"
            
        st.markdown(f'<div style=" background-color: rgba(255, 255, 255, 0.8);">Le tarif pour {nom_ville.capitalize()} est: {tarif} €</div>', unsafe_allow_html=True)
    else:
        st.write("Impossible de géocoder la ville. Veuillez vérifier l'orthographe.")

# Fonction qui garde l'application éveillée
def keep_awake():
    while True:
        time.sleep(60)
        print("L'application est toujours active...")

# Créer et démarrer le thread
thread = threading.Thread(target=keep_awake)
thread.daemon = True  # Permet au thread de s'arrêter lorsque l'application principale se termine
thread.start()