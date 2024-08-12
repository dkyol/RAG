from dp_solutions_architecture_utils.bucket import BucketUtil
import os

# The name of the bucket associated with this instance of Prospero
BUCKET_NAME = 'nvidia-prospero-test'

# Use different prefixes for different types of content 
# Need prefixes so that bucket is organized like a filesystem 
BUCKET_PREFIX = 'document_db'
bucket_util = BucketUtil(BUCKET_NAME, BUCKET_PREFIX)

# Assuming we already have some csvs for upload stored in the directory `data`
bucket_util.upload_directory('data')

# Verify the upload worked
bucket_util.list_contents()

# Download that data we just uploaded back into a new directory 
bucket_util.download('data1')

# Verify that the download worked
os.listdir('data1')