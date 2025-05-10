# The following line near the beginning of the file
def setup_minio_client():
    """Set up and return MinIO client"""
    try:
        # MinIO client setup
        minio_url = os.getenv('MINIO_URL', 'http://localhost:9000')
        # Print the URL being used for debugging
        print(f"Connecting to MinIO at: {minio_url}")
        
        s3_client = boto3.client(
            's3',
            endpoint_url=minio_url,
            aws_access_key_id=os.getenv('MINIO_USER', 'your-access-key'),
            aws_secret_access_key=os.getenv('MINIO_PASSWORD', 'your-secret-key'),
            region_name='us-east-1',
            config=boto3.session.Config(signature_version='s3v4')
        )
        
        # Test connection by listing buckets
        response = s3_client.list_buckets()
        print(f"Connected to MinIO. Available buckets: {[bucket['Name'] for bucket in response['Buckets']]}")
        return s3_client
    except Exception as e:
        print(f"Warning: Could not connect to MinIO: {e}")
        print("Will continue without storage capabilities.")
        return None