用来管理xuexiaig网站的python工具集.

## 安装依赖
该小工具有两个依赖SDK，如下：
1. COS SDK
```sh
pip install -U cos-python-sdk-v5
```
详细参考: https://cloud.tencent.com/document/product/436/12269#.E4.B8.8B.E8.BD.BD.E4.B8.8E.E5.AE.89.E8.A3.85

2. OpenAI SDK
```sh
pip install --upgrade openai
```
详细参考: https://platform.openai.com/docs/quickstart?context=python

## 配置
在运行python脚本之前，请根据需要配置下面的环境变量。
1. OPENAI_API_KEY: OpenAI API key，在生成文章的摘要时需要。
2. COS_SECRET_ID: 腾讯云对象存储COS的secret_id，需要要COS桶的读写权限。
3. COS_SECRET_KEY: 腾讯云对象存储COS的secret_key，需要要COS桶的读写权限。
4. COS_BUCKET: 腾讯云对象存储COS的存储桶，用来存储网站的素材。
5. COS_REGION: 腾讯云对象存储COS的bucket所在的区域。

## 支持的子命令
查看支持的命令请执行：
```sh
python3 webmanager.py -h
```

### webscreenshot
基于输入的文件或者命令行参数，获取网站的截图照片，并存储到COS中。
示例：
```sh
python3 webmanager.py -i https://www.xuexiaigc.com webscreenshot
```

### webvisits
基于输入的文件或者命令行参数，获取网站过去三个月的访问数据，依次判断AIGC网站的热度。
示例：
```sh
python3 webmanager.py -i https://www.xuexiaigc.com webvisits
```

### articlesummary
输入的文件或者命令行参数，获取文章的摘要，基于摘要模板输出文本，可以直接贴到后台新文章里。
示例：
```sh
python3 webmanager.py -i https://mp.weixin.qq.com/s/izteCpW1xZlyqlOws9lHsg articlesummary
```
