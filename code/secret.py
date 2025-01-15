from google.cloud import secretmanager
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"), override=True)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '../keys/auth_cloud_indicators.json'

#closure
def secrets(project_id):
    client = secretmanager.SecretManagerServiceClient()
    def request_key(secret_id, version):
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload
    return request_key