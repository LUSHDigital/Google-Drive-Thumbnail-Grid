import logging
import json, hashlib, os
import argparse
import base64
import urllib.request
from google.cloud import storage
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import requests
from io import open as iopen
import stich
from apiclient.http import MediaFileUpload

parser = argparse.ArgumentParser(description='Check for new images for Lens Model')
parser.add_argument('--team-drive-id', type=str, help='Path of the local file or GCS blob containing the Input 1 data.')
parser.add_argument('--train-gdrive-id', type=str, help='Parameter 1.')
parser.add_argument('--data-bucket', type=str, help='Path of the local file where the Output 1 URI data should be written.')
parser.add_argument('--service-account-key', type=str, help='Path of the local file where the Output 1 URI data should be written.')
args = parser.parse_args()

key = json.loads(base64.b64decode(args.service_account_key))
logging.info('Cannot decode {}. Skipping file...'.format(key))
credentials = ServiceAccountCredentials.from_json_keyfile_dict(key , "https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/drive")
drive = build('drive', 'v3', cache_discovery=False, credentials=credentials)

def print_file_metadata(drive, file_id):
    response = drive.files().get(supportsTeamDrives='true',fileId=file_id,fields='thumbnailLink').execute()
    thumbnailLink = response.get('thumbnailLink', [])
    return thumbnailLink

def fetch_gdrive_metadata(drive, team_drive_id, folder_id, parent):
    directories = {}
    pageToken = ''
    while True:
        response = drive.files().list(corpora="teamDrive",
                                      includeTeamDriveItems='true',
                                      supportsTeamDrives='true',
                                      q="'" + folder_id + "' in parents and trashed != true",
                                      teamDriveId=args.team_drive_id,
                                      pageSize='1000',
                                      fields='nextPageToken, files(name, id, parents)',
                                      pageToken=pageToken).execute()

        pageToken = response.get('nextPageToken', None)
        for file in response.get('files', []):
            label = file['name']
            try:
                id = int(label.split("_")[0])
            except:
                id = label
            gdid = file['id']
            if not id in directories:
                directories[id] = {
                    "label" : label,
                    "count" : 0,
                    "sums" : [],
                    "uris" : [],
                    "id" : id,
                    "gdid" : gdid,
                    "parent" : parent
                }

        if pageToken is None:
            break

    return directories

def imgage_download(url):
    name = "/images/" + url[url.rfind("/")+1:] + ".jpeg"
    urllib.request.urlretrieve(url, name)

def fetch_image(img_ur, parent):
    directory = "/images/" + parent + "/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    save_filename = directory + img_ur[img_ur.rfind("/")+1:] + ".jpeg"
    img = requests.get(img_ur)
    if img.status_code == 200:
        print(200)
        with iopen(save_filename, 'wb') as f:
            f.write(img.content)
    else:
        print('Received error: {}'.format(img.status_code))

grirs = fetch_gdrive_metadata(drive, args.team_drive_id, args.train_gdrive_id, "")

print(grirs)

gfiles = {}
gthumbs = {}

for dir in grirs:
    gdir = grirs[dir]["gdid"]
    glabel = grirs[dir]["label"]
    d = fetch_gdrive_metadata(drive, args.team_drive_id, gdir, glabel)
    gfiles[gdir]= d

for key, value in gfiles.items():
    for fkey, fvalue in value.items():
        gfiles = fvalue.get('gdid')
        gparent = fvalue.get('parent')
        f = print_file_metadata(drive, gfiles)
        gthumbs[gfiles] = {
            "thumb" : f,
            "gdid" : gfiles,
            "parent" : gparent
        }

for key, value in gthumbs.items():
    fetch_image(value["thumb"], value["parent"])



for dir in grirs:
    gdir = "/images/" + grirs[dir]["label"]
    grid = stich.generate(gdir)

    # file_metadata = {
    #     'name': grirs[dir]["label"] + '.jpeg',
    #     'parents': grirs[dir]["gdid"]
    # }
    # media = MediaFileUpload(grid,
    #                         mimetype='image/jpeg')
    # file = drive.files().create(body=file_metadata,
    #                             supportsAllDrives='true',
    #                             media_body=media,
    #                             fields='id').execute()
    # print('File ID: %s' % file.get('id'))

quit()
