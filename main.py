import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# rayon premier cercle : 25km
# rayon deuxième cercle : 50km
# rayon troisième cercle : 75km
# rayon quatrième cercle : 100km

geolocator = Nominatim(user_agent="equiconfort")

# Coordonnées des centres
_ = geolocator.geocode("flavigny, 57130, France")
Centre1 = (_.latitude, _.longitude)

_ = geolocator.geocode("hablainville, 54120, France")
Centre2 = (_.latitude, _.longitude)

# Titre de l'application
st.title('Equiselle - Tarif')

# Entrée du nom de la ville
nom_ville = st.text_input("Entrez le nom de la ville pour obtenir le tarif:")

if nom_ville:
    # Géocoder la ville pour obtenir ses coordonnées
    location = geolocator.geocode(nom_ville)    
    if location:
        coord_ville = (location.latitude, location.longitude)
        
        # Calculer les distances
        distance1 = geodesic(coord_ville, Centre1).km
        distance2 = geodesic(coord_ville, Centre2).km
        # st.write(f"Distance jusqu'à Centre1: {distance1:.2f} km")
        # st.write(f"Distance jusqu'à Centre2: {distance2:.2f} km")
        
        if nom_ville.lower() == "luxembourg":
            tarif = 70 
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
            
        st.write(f"Le tarif pour {nom_ville.capitalize()} est: {tarif} €")
    else:
        st.write("Impossible de géocoder la ville. Veuillez vérifier l'orthographe.")
