import streamlit as st
import folium
import networkx as nx
import osmnx as ox
from streamlit_folium import st_folium

def show():
    st.title("🚶‍♂️ Campus Navigation with Real Paths")

    # Common Campus Variables
    CAMPUS_CENTER = (13.0087, 80.0034)

    try:
        # Get the campus graph
        campus_graph = ox.graph_from_point(CAMPUS_CENTER, dist=500, network_type='walk')

        # Get node positions (latitude, longitude)
        nodes, _ = ox.graph_to_gdfs(campus_graph, nodes=True, edges=True)
        node_positions = {node: (data['y'], data['x']) for node, data in nodes.iterrows()}

        # Define important campus locations by snapping to nearest OSM nodes
        campus_locations = {
            "Hut Cafe": ox.distance.nearest_nodes(campus_graph, 80.0036, 13.0084),
            "Library": ox.distance.nearest_nodes(campus_graph, 80.0055, 13.0090),
            "Indoor Auditorium": ox.distance.nearest_nodes(campus_graph, 80.0055, 13.0084),
            "REC Cafe": ox.distance.nearest_nodes(campus_graph, 80.0026, 13.0086),
            "Ground": ox.distance.nearest_nodes(campus_graph, 80.0044, 13.0085),
            "Basket Ball Court": ox.distance.nearest_nodes(campus_graph, 80.0041, 13.0093),
        }

        # User selects source and destination
        source_name = st.selectbox("Select Source", list(campus_locations.keys()))
        destination_name = st.selectbox("Select Destination", list(campus_locations.keys()))

        # Get nearest OSM nodes for selected buildings
        source = campus_locations[source_name]
        destination = campus_locations[destination_name]

        # Compute the shortest path using A* algorithm
        if nx.has_path(campus_graph, source, destination):
            shortest_path = nx.shortest_path(campus_graph, source, destination, weight="length")
        else:
            shortest_path = [source, destination]  # Direct path if no alternative

        # Convert path node IDs to (lat, lon) coordinates
        path_coords = [node_positions[node] for node in shortest_path]

        # Create Folium map centered at the source
        campus_map = folium.Map(location=node_positions[source], zoom_start=18, tiles="OpenStreetMap")

        # Add markers for source and destination
        folium.Marker(node_positions[source], popup=f"📍 {source_name} (Start)", icon=folium.Icon(color="green")).add_to(campus_map)
        folium.Marker(node_positions[destination], popup=f"🎯 {destination_name} (End)", icon=folium.Icon(color="blue")).add_to(campus_map)

        # Draw the route following real roads
        folium.PolyLine(path_coords, color="blue", weight=5, opacity=0.7).add_to(campus_map)

        # Display the map
        st_folium(campus_map, width=800, height=600)
    
    except Exception as e:
        st.error(f"Error in campus navigation: {e}")
        st.warning("Please make sure you have the necessary libraries installed. If this is a demo, you can view the map without real data.")
        
        # Display a placeholder map if there's an error
        st.write("Placeholder map showing route from Library to Cafeteria")
        basic_map = folium.Map(location=[13.0087, 80.0034], zoom_start=16)
        st_folium(basic_map, width=800, height=600)

if __name__ == "__main__":
    # Setup for standalone run
    st.set_page_config(page_title="Campus Navigation", page_icon="🚶‍♂️")
    show()
