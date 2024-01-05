from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from qcloud_cos import CosClientError

class COSClient:
    def __init__(self, secret_id, secret_key, region, bucket, token=None):
        cos_config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token)
        self._bucket = bucket
        self._region = region
        self._client = CosS3Client(cos_config)

    def get_object_url(self, key):
        ourl = "https://" + self._bucket + ".cos." + self._region + ".myqcloud.com/" + key
        return ourl

    def does_object_exist(self, key):
        try:
            object_info = self._client.head_object(self._bucket, key)
        except Exception as e:
            #print(str(e))
            return None
        return object_info

    def upload_object_from_file(self, fpath, okey):
        try:
            response = self._client.upload_file(
                    Bucket=self._bucket,
                    Key=okey,
                    LocalFilePath=fpath,
                    PartSize=100,
                    MAXThread=10,
                )
        except Exception as e:
            print(str(e))
            return False
        return True

    def ci_image_process(self, okey, operations):
        try:
            response, data = self._client.ci_image_process(
                    Bucket=self._bucket,
                    Key=okey,
                    PicOperations=operations
                )
        except Exception as e:
            print(str(e))
            return None, None
        return response, data

