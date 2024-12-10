import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import streamlit as st
import json

def run_zone_selection():
    """
    Streamlit app for selecting a zone on a map.
    Returns:
        dict: A dictionary containing the selected area's center and radius.
    """
    st.title("Zone Selection Tool")
    st.markdown("""
    **Instructions:**
    - Use the **Circle** drawing tool to select an area.
    - **Maximum allowed radius is 1 km.**
    """)

    # Initialize map
    m = folium.Map(location=[-14.235, -51.9253], zoom_start=5)

    # Add drawing tools
    draw = Draw(
        draw_options={
            "polyline": False,
            "polygon": False,
            "circle": True,
            "rectangle": False,
            "marker": False,
        },
        edit_options={"edit": False},
    )
    draw.add_to(m)

    # Display map
    st_data = st_folium(m, width=700, height=500)

    # Check for user input
    if st_data.get("last_active_drawing"):
        drawing = st_data["last_active_drawing"]
        geometry_type = drawing.get("geometry", {}).get("type", None)

        if geometry_type == "Point" and "radius" in drawing["properties"]:
            center = drawing["geometry"]["coordinates"]
            radius = drawing["properties"]["radius"]

            max_radius = 1000  # 1 km in meters
            if radius <= max_radius:
                selected_area = {
                    "center": {"lat": center[1], "lon": center[0]},
                    "radius": radius,
                }

                # Save to JSON file
                with open("selected_area.json", "w") as f:
                    json.dump(selected_area, f)
                    

                st.success("Area successfully saved!")
                st.json(selected_area)  # Display the saved area
                return selected_area
            else:
                st.error(f"Radius exceeds the maximum limit of {max_radius} meters.")
        else:
            st.warning("Please use the Circle tool to select an area.")
    else:
        st.info("Use the Circle tool on the map to select an area.")

    return None
run_zone_selection()