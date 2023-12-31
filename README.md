A command-line tool used to manage xuexiaigc website.

## Install
Before run this tool, you need install two related SDK.
1. COS SDK
```sh
pip install -U cos-python-sdk-v5
```
More information in: https://cloud.tencent.com/document/product/436/12269#.E4.B8.8B.E8.BD.BD.E4.B8.8E.E5.AE.89.E8.A3.85

2. OpenAI SDK
```sh
pip install --upgrade openai
```
More information in: https://platform.openai.com/docs/quickstart?context=python

## Configuration
Please configurate below envionment variables firstly.
1. OPENAI_API_KEY: OpenAI API key, used to generate artical summary.
2. COS_SECRET_ID: Tencent COS secret id, need has priorities to read/write COS Bucket.
3. COS_SECRET_KEY: Tencent COS secret key, need has priorities to read/write COS Bucket.
4. COS_BUCKET: Tencent COS bucket, used to store some website materials.
5. COS_REGION: Tencent COS region, where bucket created.

## Sub Commands
### webscreenshot
Get website screenshot and stored it in COS.
Example:
```sh
python3 webmanager.py -i https://www.xuexiaigc.com webscreenshot
```

### webvisits
Get website visits in latest three months.
Example:
```sh
python3 webmanager.py -i https://www.xuexiaigc.com webvisits
```

### articlesummary
Get article summary and generate formated text used to paste in xuexiaigc.
Example:
```sh
python3 webmanager.py -i https://mp.weixin.qq.com/s/izteCpW1xZlyqlOws9lHsg articlesummary
```
