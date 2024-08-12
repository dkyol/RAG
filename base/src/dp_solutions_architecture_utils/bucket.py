import boto3
import os 


class BucketUtil:
    """
    AWS S3 Utility class for uploading to/downloading from buckets. 
    See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html for original API docs.
    """
    
    def __init__(self, bucket_name, prefix):
        self.bucket_name = bucket_name
        self.prefix = prefix
        
    def _check_inputs(self, file_paths, object_names):
        # wrap file_paths and object_names if strings are passed in
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        if isinstance(object_names, str):
            object_names = [object_names]
            
        if len(file_paths) != len(object_names):
            raise Exception(f"file_paths must be same length as object_names. Got {len(file_paths)} and {len(object_names)}")
            
        return file_paths, object_names
        
    def upload_directory(self, directory, object_names=None):
        file_names = os.listdir(directory)
        file_paths = [os.path.join(directory, file_name) for file_name in file_names]
        if object_names is None:
            object_names = file_names
        self.upload(file_paths, object_names)
        
    def upload(self, file_paths, object_names):
        """
        :param str or List[str]: file_paths: file paths to object(s) that will be uploaded to the bucket.
        :param str or List[str]: object_names key names for the object(s) in the bucket. Should NOT include prefix.
        """
        file_paths, object_names = self._check_inputs(file_paths, object_names)
        
        s3 = boto3.resource('s3')
            
        for file_path, object_name in zip(file_paths, object_names):
            with open(file_path, 'rb') as data:
                s3.Bucket(self.bucket_name).put_object(Key=f'{self.prefix}/{object_name}', Body=data)
            print(f'Uploaded {file_path} to bucket {self.bucket_name} under key {self.prefix}/{object_name}')
            
    def list_contents(self):
        """
        Get list of files availfor this bucket/prefix combo.
        """
        s3_client = boto3.client("s3")
        response = s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.prefix)
        files = response.get("Contents")
        return files
    
    def download(self, directory, object_names=None):
        """
        :param str: directory: Local directory to store downloaded objects.
        :param str or List[str]: object_names key names for the object(s) in the bucket. Should NOT include prefix.
        """
        if object_names is None:
            files = self.list_contents()
            object_names = [file['Key'] for file in files]
        else: 
            object_names = [f'{self.prefix}/{object_name}' for object_name in object_names]
        
        file_paths = [os.path.join(directory, object_name[len(self.prefix) + 1:]) for object_name in object_names]
        for file_path in file_paths:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        s3_client = boto3.client("s3")
        
        for file_path, object_name in zip(file_paths, object_names):
            s3_client.download_file(self.bucket_name, object_name, file_path)
            print(f'Downloaded object {object_name} from bucket {self.bucket_name} to {file_path}')
