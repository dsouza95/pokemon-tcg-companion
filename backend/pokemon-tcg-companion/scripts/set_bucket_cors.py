from google.cloud import storage

from core.settings import settings

client = storage.Client()
bucket = client.bucket(settings.gcp_bucket)
bucket.cors = [
    {
        "origin": settings.allowed_origins.split(","),
        "method": ["GET", "PUT", "POST", "OPTIONS"],
        "responseHeader": ["Content-Type", "Content-MD5", "x-goog-resumable"],
        "maxAgeSeconds": 3600,
    }
]
bucket.patch()
