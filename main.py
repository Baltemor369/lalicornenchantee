import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Coordonnées des centres
Centre1 = (49.14524698873021, 6.108990297508489)
Centre2 = (48.55194848812558, 6.745914470401151)

# Titre de l'application
st.title('Tarifs et Distances des Villes')

# Entrée du nom de la ville
nom_ville = st.text_input("Entrez le nom de la ville pour obtenir le tarif et calculer la distance:")

if nom_ville:
    # tarif = villes_tarifs.get(nom_ville, "Ville non trouvée")
    # st.write(f"Le tarif pour {nom_ville} est: {tarif} €")
    
    # Géocoder la ville pour obtenir ses coordonnées
    geolocator = Nominatim(user_agent="equiconfort")
    location = geolocator.geocode(nom_ville)
    
    if location:
        coord_ville = (location.latitude, location.longitude)
        st.write(f"Coordonnées de {nom_ville.capitalize()}: {coord_ville}")
        
        # Calculer les distances
        distance1 = geodesic(coord_ville, Centre1).km
        distance2 = geodesic(coord_ville, Centre2).km
        st.write(f"Distance jusqu'à Centre1: {distance1:.2f} km")
        st.write(f"Distance jusqu'à Centre2: {distance2:.2f} km")
    else:
        st.write("Impossible de géocoder la ville. Veuillez vérifier l'orthographe.")
