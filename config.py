import os

# only UPPERCASE_NAMES are considered as configuration keys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'main.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')

CRSF_ENABLED = True
SECRET_KEY = 'change_this_later_please'

S3_UPLOAD_CMD = 'AWS_ACCESS_KEY_ID=AKIAIPQWPD27UVERPCXQ AWS_SECRET_ACCESS_KEY=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 aws s3 cp %s %s --region=ap-southeast-1 --acl=public-read'
S3_IMGZIP_LOCATION = 's3://remidi-v2/images/'
S3_IMGZIP_URL = 'https://s3-ap-southeast-1.amazonaws.com/remidi-v2/images/'

HIDE_MICROSCOPIST_FROM_VALIDATOR = True
LONGLAT_PRECISION_PT = 2

GMAPS_APIKEY = 'PutAPIKeyHere'
