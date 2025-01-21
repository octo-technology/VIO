from pydantic import BaseModel


class AWSCreds(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str
    bucket_name: str
