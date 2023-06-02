import os

from pydantic import BaseSettings


class ServiceEnv(BaseSettings):
    ROOT_DIR: str = os.path.join(os.path.expanduser("~"), "whisper_service")
    UPLOAD_DIR: str = os.path.join(ROOT_DIR, "upload")
    DOWNLOAD_DIR: str = os.path.join(ROOT_DIR, "download")


SERVICE_ENV = ServiceEnv()

# init project
if not os.path.exists(SERVICE_ENV.ROOT_DIR):
    os.makedirs(SERVICE_ENV.ROOT_DIR)

if not os.path.exists(SERVICE_ENV.UPLOAD_DIR):
    os.makedirs(SERVICE_ENV.UPLOAD_DIR)

if not os.path.exists(SERVICE_ENV.DOWNLOAD_DIR):
    os.makedirs(SERVICE_ENV.DOWNLOAD_DIR)
