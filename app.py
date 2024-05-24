import streamlit as st
from datetime import datetime
import requests
import pandas as pd
import pydeck as pdk

'''
# NY Taxi Fare Predictor
'''


with st.form("input_form"):
    pickup_date = st.date_input('Pickup date', value= datetime.now())
    pickup_time = st.time_input('Pickup time',value= datetime.now())

    pickup_longitude = st.text_input(label="Pickup longitude",value=-73.950655)
    pickup_latitude = st.text_input(label="Pickup latitude",value=40.783282)

    dropoff_longitude = st.text_input(label="Drop-off longitude",value=-73.984365)
    dropoff_latitude = st.text_input(label="Drop-off latitude",value=40.769802)

    passenger_count = st.selectbox(
        label="Passenger count",
        options=range(1,9))

    submit = st.form_submit_button('Submit')

    url = 'https://taxifare.lewagon.ai/predict'

    if submit:
        combined_datetime = datetime.combine(pickup_date, pickup_time)
        if url == 'https://taxifare.lewagon.ai/predict':
            params = {
            "pickup_datetime": combined_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "pickup_longitude": float(pickup_longitude),
            "pickup_latitude": float(pickup_latitude),
            "dropoff_longitude": float(dropoff_longitude),
            "dropoff_latitude": float(dropoff_latitude),
            "passenger_count": passenger_count
            }
            response = requests.get(url=url,params=params,timeout=10)
            if response.status_code == 200:
                result = response.json()
                st.title(f"Predicted Fare: ${result['fare']:.2f}")
            else:
                st.error("Fai`led to get response from the server.")


            # Get directions from Mapbox Directions API
            directions_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{params['pickup_longitude']},{params['pickup_latitude']};{params['dropoff_longitude']},{params['dropoff_latitude']}"
            directions_params = {
                "geometries": "geojson",
                "access_token": st.secrets.mapbox_api_key
            }
            directions_response = requests.get(directions_url, params=directions_params)
            if directions_response.status_code == 200:
                directions_data = directions_response.json()
                route = directions_data["routes"][0]["geometry"]["coordinates"]

                # Data for the map
                data = pd.DataFrame(route, columns=['lon', 'lat'])

                # Adding the pickup and dropoff points
                points = pd.DataFrame({
                    'lat': [params['pickup_latitude'], params['dropoff_latitude']],
                    'lon': [params['pickup_longitude'], params['dropoff_longitude']],
                    'name': ['Pickup', 'Dropoff']
                })

                # Map view state
                view_state = pdk.ViewState(
                    latitude=(params['pickup_latitude'] + params['dropoff_latitude']) / 2,
                    longitude=(params['pickup_longitude'] + params['dropoff_longitude']) / 2,
                    zoom=12,
                    pitch=50,
                )

                # Route layer
                route_layer = pdk.Layer(
                    'PathLayer',
                    data,
                    get_path='[lon, lat]',
                    width_scale=20,
                    width_min_pixels=2,
                    width_max_pixels=5
                )
                # Points layer
                points_layer = pdk.Layer(
                    'ScatterplotLayer',
                    points,
                    get_position='[lon, lat]',
                    get_radius=200,
                )

                # Map Deck
                r = pdk.Deck(
                    map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=view_state,
                    layers=[route_layer, points_layer],
                    api_keys={'mapbox': st.secrets.mapbox_api_key}
                )

                # Display map
                st.pydeck_chart(r)
            else:
                st.error("Failed to get directions from Mapbox.")
