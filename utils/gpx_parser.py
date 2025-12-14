import gpxpy
import gpxpy.gpx
import polyline
import math
from datetime import datetime

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def parse_gpx_to_strava_format(file_stream):
    gpx = gpxpy.parse(file_stream)
    
    track_points = []
    for track in gpx.tracks:
        for segment in track.segments:
            track_points.extend(segment.points)

    if not track_points:
        return None

    # Streams
    latlngs = []
    altitudes = []
    heartrates = []
    cadences = []
    temperatures = []
    powers = []
    times = [] # in seconds from start
    distances = [] # cumulative distance
    
    start_time = track_points[0].time
    total_distance = 0
    total_elevation_gain = 0
    max_speed = 0
    max_hr = 0
    max_cadence = 0
    max_watts = 0
    prev_point = None
    elev_high = -float('inf')
    
    for point in track_points:
        latlngs.append([point.latitude, point.longitude])
        altitudes.append(point.elevation)
        if point.elevation > elev_high:
            elev_high = point.elevation
            
        # Extensions handling (HR, Cadence, Power, Temp)
        hr = None
        cad = None
        temp = None
        watts = None
        
        for extension in point.extensions:
            # Handle standard GPX extensions (Garmin usually)
            if 'TrackPointExtension' in extension.tag:
                for child in extension:
                    if 'hr' in child.tag:
                        try: hr = int(child.text)
                        except: pass
                    elif 'cad' in child.tag:
                        try: cad = int(child.text)
                        except: pass
                    elif 'atemp' in child.tag:
                        try: temp = float(child.text)
                        except: pass
            # Handle Power (often separate)
            if 'power' in extension.tag:
                 try: watts = float(extension.text)
                 except: pass

        if hr: 
            heartrates.append(hr)
            if hr > max_hr: max_hr = hr
        else:
            heartrates.append(None) # Maintain indices
            
        if cad:
            cadences.append(cad)
            if cad > max_cadence: max_cadence = cad
        else:
            cadences.append(None)

        if watts:
            powers.append(watts)
            if watts > max_watts: max_watts = watts
        else:
            powers.append(None)
            
        if temp:
            temperatures.append(temp)
        else:
            temperatures.append(None)

        # Distance & Time
        dist_inc = 0
        if prev_point:
            dist_inc = haversine_distance(prev_point.latitude, prev_point.longitude, point.latitude, point.longitude)
            total_distance += dist_inc
            
            # Simple elevation gain
            ele_diff = point.elevation - prev_point.elevation
            if ele_diff > 0:
                total_elevation_gain += ele_diff
                
            # Speed calc (instant)
            time_diff = (point.time - prev_point.time).total_seconds()
            if time_diff > 0:
                speed = dist_inc / time_diff
                if speed > max_speed: max_speed = speed
        
        distances.append(total_distance)
        times.append((point.time - start_time).total_seconds())
        prev_point = point

    # Moving time (simplified: total elapsed for now, or filter stops)
    elapsed_time = int((track_points[-1].time - start_time).total_seconds())
    moving_time = elapsed_time # Rough approximation
    
    # Averages
    avg_speed = total_distance / moving_time if moving_time > 0 else 0
    avg_hr = sum(filter(None, heartrates)) / len(list(filter(None, heartrates))) if any(heartrates) else None
    avg_cadence = sum(filter(None, cadences)) / len(list(filter(None, cadences))) if any(cadences) else None
    avg_watts = sum(filter(None, powers)) / len(list(filter(None, powers))) if any(powers) else None

    # Summary Polyline
    summary_polyline = polyline.encode(latlngs)

    # Normalize structure to Strava API format
    streams = {
        'latlng': latlngs,
        'altitude': altitudes,
        'time': times,
        'distance': distances,
        'heartrate': heartrates if any(heartrates) else None,
        'cadence': cadences if any(cadences) else None,
        'watts': powers if any(powers) else None,
        'temp': temperatures if any(temperatures) else None,
        'velocity_smooth': [] # Optional to derive from distance/time
    }
    
    # Clean up None streams
    streams = {k: v for k, v in streams.items() if v is not None}

    return {
        'id': f"gpx_{int(start_time.timestamp())}",
        'name': gpx.tracks[0].name or "Uploaded Activity",
        'distance': total_distance,
        'moving_time': moving_time,
        'elapsed_time': elapsed_time,
        'total_elevation_gain': total_elevation_gain,
        'elev_high': elev_high,
        'average_speed': avg_speed,
        'max_speed': max_speed,
        'average_heartrate': avg_hr,
        'max_heartrate': max_hr,
        'average_cadence': avg_cadence,
        'max_cadence': max_cadence,
        'average_watts': avg_watts,
        'max_watts': max_watts,
        'start_date': start_time.isoformat(),
        'start_latlng': latlngs[0] if latlngs else None,
        'map': {
             'summary_polyline': summary_polyline
        },
        'streams': streams,
        'source': 'gpx',
        'type': 'Run' # Default to Run for GPX
    }
