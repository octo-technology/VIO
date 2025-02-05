from pydantic import BaseModel


class GCPCreds(BaseModel):
    gcp_credentials: str
    bucket_name: str
