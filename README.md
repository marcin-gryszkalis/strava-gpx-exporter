# Strava-GPX-exporter
Download all GPX from your Strava account


## Prerequisite

- pandas

## Set-up

Before you run the script, make sure you create your API application [here](https://www.strava.com/settings/api).

Put `localhost` for `Authorization Callback domain`. For other fields, it doesn't really matter whatever you fill in.

You might find [this article](https://towardsdatascience.com/using-the-strava-api-and-pandas-to-explore-your-activity-data-d94901d9bfde) useful as a reference when setting up your first Strava API app.

When you run `python strava_gpx.py` for the first time, the prompt will ask you to fill in your `client_id` and `client_secret`, which you should have got by now on your [API page](https://www.strava.com/settings/api).

Your client ID and secret are only saved on your computer locally and will never be shared with others.

Follow the prompt to finish the remainder of the one-time set-up process. 

## Usuages

Download the GPX of your latest activity

```
python strava_gpx.py
```

Download the GPX of your latest N activities

Say, you want to download your recent 50 activities:

```
python strava_gpx.py 50
```

Current limit is `99` due to Strava API's rate limit.

Once the download completes, the gpx files can be found under `gpx/`.
