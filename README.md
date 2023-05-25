# Strava GPX exporter
Download all GPX from your Strava account

## Setup

Before you run the script, make sure you create your API application [here](https://www.strava.com/settings/api).

Put `localhost` for `Authorization Callback domain`. For other fields, it doesn't really matter whatever you fill in.

You might find [this article](https://towardsdatascience.com/using-the-strava-api-and-pandas-to-explore-your-activity-data-d94901d9bfde) useful as a reference when setting up your first Strava API app.

When you run `python strava_gpx.py` for the first time, the prompt will ask you to fill in your `client_id` and `client_secret`, which you should have got by now on your [API page](https://www.strava.com/settings/api).

Your client ID and secret are only saved on your computer locally and will never be shared with others.

Follow the prompt to finish the remainder of the one-time set-up process. 

## Usage

Download all gpx files from strava account

```
python strava_gpx.py
```

Once the download completes, the gpx files can be found under `gpx/`.

## Limits

Script tries to adhere to default Strava limits (1000 API calls per day, 100 per 15 minutes) but it may still fail if you run the script several times (as usage is not persistent between runs).

## Authors
The script was forked from https://github.com/liponan/Strava-GPX-exporter although it worked differently, gpx creation was limited and so on (but it had nice working authentication part). Thus I decided to split from original one.
