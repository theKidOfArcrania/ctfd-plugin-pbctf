import os
import os.path
import string
import sys

from flask import current_app, redirect
from google.oauth2 import service_account
from google.cloud import storage
from werkzeug.utils import secure_filename

from CTFd.utils import get_app_config
from CTFd.utils.uploads import UPLOADERS
from CTFd.utils.uploads.uploaders import BaseUploader
from CTFd.utils.encoding import hexencode

# Requires setting GCP_STORE_CRED and GCP_STORE_BUCKET vars
# and GCP_STORE_CRED should be a json file for our private key creds
#
# Should also modify the requirements.in and requiremnts.txt file to have
# google-cloud-storage==1.33.0 dependency

class GCPUploader(BaseUploader):
    def __init__(self):
        super(BaseUploader, self).__init__()
        self.gcp = storage.Client.from_service_account_json(
                get_app_config('GCP_STORE_CRED'))
        self.bucket = self.gcp.get_bucket(get_app_config("GCP_STORE_BUCKET"))


    def _clean_filename(self, c):
        if c in string.ascii_letters + string.digits + "-" + "_" + ".":
            return True

    def store(self, fileobj, filename):
        blob = self.bucket.blob(filename)
        blob.upload_from_file(fileobj)
        blob.make_public()
        return filename

    def upload(self, file_obj, filename):
        filename = filter(
            self._clean_filename, secure_filename(filename).replace(" ", "_")
        )
        filename = "".join(filename)
        if len(filename) <= 0:
            return False

        md5hash = hexencode(os.urandom(16))

        dst = md5hash + "/" + filename
        return self.store(file_obj, dst)

    def download(self, filename):
        blob = self.bucket.blob(filename)
        return redirect(blob.public_url)

    def delete(self, filename):
        try:
            # Might have an error if it's not there
            blob = self.bucket.blob(filename)
            blob.delete()
        except:
            import traceback
            traceback.print_exc(file=sys.stdout)

    def sync(self):
        local_folder = current_app.config.get("UPLOAD_FOLDER")
        for blob in self.bucket.list_blobs():
            if blob.name.endswith("/") is False:
                local_path = os.path.join(local_folder, blob.name)
                directory = os.path.dirname(local_path)
                if not os.path.exists(directory):
                    os.makedirs(directory)

                blob.download_to_file(local_path)

def load(app):
    UPLOADERS['gcp'] = GCPUploader
