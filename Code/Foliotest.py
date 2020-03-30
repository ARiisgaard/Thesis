import folium
from folium.plugins import DualMap
folder = 'C:\\Users\\Public\\Python\\Git\\Thesis\\Thesis\\Code\\'


#Single Map
# m = folium.Map(location=[45.5236, -122.6750], zoom_start=12)

#Dual Map
m = DualMap(location=(45.5236, -122.6750), tiles=None,
            zoom_start=12)
folium.TileLayer('openstreetmap').add_to(m.m1) #Replace these with urls for the server, when up
folium.TileLayer('stamenwatercolor').add_to(m.m2)
# folium.LayerControl().add_to(m)


#Creating a file with the result
m.save(folder + 'Virker.html')