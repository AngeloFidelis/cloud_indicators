from google.cloud import secretmanager

#closure
def secrets(project_id):
    client = secretmanager.SecretManagerServiceClient()
    def request_key(secret_id, version):
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload
    return request_key