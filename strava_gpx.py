import requests
import json
import pandas as pd
import os
import re
import sys
import time
import itertools

def get_credential():
    if not (os.path.isfile("CLIENT_ID") and os.path.isfile("CLIENT_SECRET")):
        get_credential_from_user()
    client_id = open("CLIENT_ID", "r").read()
    client_secret = open("CLIENT_SECRET", "r").read()
    return client_id, client_secret


def get_credential_from_user():
    print("Visit https://www.strava.com/settings/api")
    print("Your Client ID: ", end="")
    client_id = input().strip()
    with open("CLIENT_ID", "w") as f:
        f.write(client_id)
    print("Client Secret: ", end="")
    client_secret = input().strip()
    with open("CLIENT_SECRET", "w") as f:
        f.write(client_secret)


def get_access_token(client_id, client_secret):
    if os.path.isfile("token.json"):
        token_json = json.load(open("token.json"))
    else:
        code = get_access_code(client_id)
        url = f"https://www.strava.com/oauth/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code"
        r = requests.post(url)
        if r.status_code == 200:
            api_response = json.loads(r.text)
            with open("token.json", "w") as f:
                json.dump(api_response, f)
        else:
            print("Error occurred when getting an access code:", r.status_code)
            return -1


def get_access_code(client_id):
    url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri=http://localhost&response_type=code&scope=activity:read_all"
    print("Copy the following URL and paste in your browser's URL space, then 'Authorize':")
    print(url)
    print("Once you see an 'error page', copy the URL in the browser and paste here: ", end="")
    raw_url = input().strip()
    pat = re.compile('&code=([\da-z]+)&')
    code = pat.findall(raw_url)[0]
    return code


def get_short_lived_token(client_id, client_secret):
    api_response = json.load(open("token.json"))
    if time.time() >= api_response["expires_at"]:
        get_long_lived_token(client_id, client_secret, api_response["refresh_token"])
        api_response = json.load(open("token.json"))
    payload = {'Authorization': f'Bearer {api_response["access_token"]}'}
    return payload


def get_long_lived_token(client_id, client_secret, refresh_token):
    url = f"https://www.strava.com/oauth/token?client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}&grant_type=refresh_token"
    r = requests.post(url)
    if r.status_code == 200:
        api_response = json.loads(r.text)
        with open("token.json", "w") as f:
            json.dump(api_response, f)
        print("Successfully retrived a new access token")
    else:
        print("Error occurred when getting a long-lived token:", r.status_code)
        return -1


def list_activities(payload, n=1, p=1):
    url = f"https://www.strava.com/api/v3/athlete/activities"
    param = {'per_page': n, 'page': p}
    r = requests.get(url, headers=payload, params=param)
    if r.status_code == 200:
        activities = r.json()
        df = pd.DataFrame(activities)
        df = df[["start_date", "id", "type", "name"]]
        return df
    else:
        print("Error occurred when getting activity list:", r.status_code)
        return -1


def download_all(payload, df):
    os.makedirs("gpx", exist_ok=True)
    for i in range(len(df)):
        activity_id, activity_name = df.iloc[i][["id", "name"]]
        output_filename = f"gpx/{activity_id} {activity_name.replace('/', '_')}.gpx"
        if os.path.isfile(output_filename):
            continue
        stream_data = get_activity_stream(activity_id, payload)
        stream2gpx(stream_data, output_filename, activity_name)


def get_activity_stream(activity_id, payload):
    url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
    print(url, end="  ")
    # for "moving" (pause logic) you may check https://github.com/cpfair/tapiriik/blob/master/tapiriik/services/Strava/strava.py
    keys = ["latlng", "altitude", "time", "heartrate", "cadence", "temp", "watts", "moving"]
    param = {"keys": ",".join(keys)}
    try:
        r = requests.get(url, headers=payload, params=param)
        print(r.status_code)
        j = json.loads(r.text)
    except:
        print(f"error occurred when fetching {activity_id} ")
        return {"latlng": [], "altitude": []}

    res = {}
    for k in keys:
        res[k] = []

    for s in j:
        print(s["type"])
        res[s["type"]] = s["data"]

    return res;


def tpxf(name, value):
    if not value:
        return ""
    return f"<gpxtpx:{name}>{value}</gpxtpx:{name}>"


def stream2gpx(stream_data, output_filename, activity_name="Strava Activity"):
    if len(stream_data["latlng"]) < 2:
        return -1
    try:
        with open(output_filename, "w") as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx creator="Strava-GPX-Exporter" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd" version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">
<metadata>
    <name>{activity_name}</name>
</metadata>
<trk>
    <name>{activity_name}</name>
    <trkseg>
""")

            for (lat, lon), time, alt, hr, cad, temp, power in itertools.zip_longest(stream_data["latlng"], stream_data["time"], stream_data["altitude"], stream_data["heartrate"], stream_data["cadence"], stream_data["temp"], stream_data["watts"]):
                rtime = time # 2023-04-10T14:06:42+00:00
                print(f"{time} {rtime}")
                f.write(f"""
<trkpt lat="{lat}" lon="{lon}">
    <time>{rtime}</time>
    <ele>{alt}</ele>
    <extensions>
      <gpxtpx:TrackPointExtension>
          {tpxf('hr',hr)}
          {tpxf('cad',cad)}
          {tpxf('temp',temp)}
          {tpxf('power',power)}
      </gpxtpx:TrackPointExtension>
    </extensions>
</trkpt>
""")
            f.write("    </trkseg>\n</trk>\n</gpx>")
    except Exception as ex:
        print(f"error occurred when exporting {output_filename}: {type(ex)=}, {ex=}")


def main():
    n = 1
    p = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        if len(sys.argv) > 2:
            p = int(sys.argv[2])

    client_id, client_secret = get_credential()
    get_access_token(client_id, client_secret)
    payload = get_short_lived_token(client_id, client_secret)
    df = list_activities(payload=payload, n=n, p=p)
    print(df)
    download_all(payload=payload, df=df)


if __name__ == "__main__":
    main()