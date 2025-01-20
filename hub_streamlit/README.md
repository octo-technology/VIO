Running the hub

Complete the .env file with the necessary information.
- `GCP_BUCKET_NAME` is the name of the bucket where the data is stored.
- `GOOGLE_APPLICATION_CREDENTIALS` is the path to the json file with the credentials to access the bucket.

Run the following commands in the terminal in the hub_streamlit directory:

    make env 
    make run

