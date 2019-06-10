# Google-Drive-Thumbnail-Grid

## Usage

Create a `.env` file by cloning the `.env.example` and set your variables:

**SERVICE_ACCOUNT_KEY** - Base64 encoded [GCP Service Account Key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).
**TEAM_DRIVE_ID** -
**TRAIN_GDRIVE_ID** -

`python ./generte_canvas.py --team-drive-id ${TEAM_DRIVE_ID} --train-gdrive-id ${TRAIN_GDRIVE_ID} --service-account-key ${SERVICE_ACCOUNT_KEY}`
