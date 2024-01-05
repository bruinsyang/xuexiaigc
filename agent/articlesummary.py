import os
import re
import math
import requests
import html2text
import urllib.parse
import hashlib
from common.agent import Agent
from bs4 import BeautifulSoup

class ArticleSummaryAgent(Agent):
    def __init__(self, cos_client, cos_prefix, openai_agent, output, log_fd):
        Agent.__init__(self, output, log_fd)
        self._cos_client = cos_client
        self._cos_prefix = cos_prefix
        self._openai_agent = openai_agent

    def count_words_and_characters(self, text):
        chinese_characters = re.findall(r'[\u4e00-\u9fff]', text)
        english_words = re.findall(r'\b[a-zA-Z]+\b', text)

        chinese_count = len(chinese_characters)
        english_count = len(english_words)
        return chinese_count + english_count

    def url2document(self, url):
        document = {}
        response = requests.get(url)
        html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")
        body = soup.find(class_="rich_media_area_primary_inner")
        title = body.find(class_="rich_media_title").text.strip()
        document['title'] = title

        doc_author = {}
        author = body.find(class_="rich_media_meta rich_media_meta_nickname").a.text.strip()
        doc_author['name'] = author
        profile_metas = body.find_all(class_="profile_meta")
        doc_author['profile'] = {}
        for meta in profile_metas:
            label = meta.find(class_="profile_meta_label").text.strip()
            value = meta.find(class_="profile_meta_value").text.strip()
            doc_author['profile'][label] = value
        document['author'] = doc_author

        content_p = body.find(class_="rich_media_content")
        try:
            wxw_img = content_p.find(class_="rich_pages wxw-img").get('data-src')
            document['image'] = wxw_img
        except Exception as e:
            try:
                wxw_img = content_p.find(class_="rich_pages wxw-img js_insertlocalimg").get('data-src')
                document['image'] = wxw_img
            except Exception as e:
                document['image'] = ''

        article_html = str(content_p)
        markdown_content = html2text.html2text(article_html, bodywidth=0)
        document['words'] = str(self.count_words_and_characters(markdown_content))
        document['content'] = markdown_content
        #print(document)
        return document

    def get_content_tags(self, doc_content):
        system_content = "你的任务是对输出的文本提取人工智能相关的关键词，请以、分隔标签，返回5个最符合的科技类标签，每个标签不超过4个字符，不要返回其他任何修饰类词语。"
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": doc_content},
        ]
        response = self._openai_agent.chat_with_openai(messages)
        result = response.choices[0].message.content
        #print(result)
        if result:
            tlist = result.split('、') 
            return tlist
        else:
            return None

    def get_content_summary(self, doc_content):
        system_content = "你的任务是对输入的文本进行总结，并给出多个段落的简短摘要。"
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": doc_content},
        ]
        response = self._openai_agent.chat_with_openai(messages)
        result = response.choices[0].message.content

        while response.choices[0].finish_reason == 'length':
            messages.append({"role": "user", "content": response.choices[0].message.content})
            response = self._openai_agent.chat_with_openai(messages)
            if response == None:
                break

            result += response.choices[0].message.content

        #print("Total result:", result)
        return result

    def get_suitable_content(self, src_content, max_length):
        content = ""
        total_characters = 0
        lines = src_content.split('\n')
        for line in lines:
            line = line.strip()
            line_characters = len(line)
            total_characters += line_characters

            if total_characters > max_length:
                break
            content += line
        return content

    def get_file_suitable_content(self, file_path, max_length):
        content = ""
        total_characters = 0
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                line_characters = len(line)
                total_characters += line_characters

                if total_characters > max_length:
                    break
                content += line
        return content

    def generate_uuid(self, input_string, uuid_length=18):
        hash_object = hashlib.sha256(input_string.encode("utf-8"))
        hash_hex = hash_object.hexdigest()
        return hash_hex[:uuid_length]

    def upload_article_image(self, image_url):
        #print(image_url)
        if len(image_url) == 0:
            return None
        image_name = self.generate_uuid(image_url) + ".jpeg"
        try:
            urllib.request.urlretrieve(image_url, image_name)
            okey = self._cos_prefix + image_name
            self._cos_client.upload_object_from_file(image_name, okey)
            os.remove(image_name)
            return self._cos_client.get_object_url(okey)
        except Exception as e:
            print(e)
            return None

    def generate_linkable_tags(self, tags):
        linkable_tags = []
        for tag in tags:
            encode_tag = urllib.parse.quote(tag)
            linkable_tags.append(f'<a href="https://www.xuexiaigc.com/?s={encode_tag}">{tag}</a>')
        return '、'.join(linkable_tags)

    def generate_website_article(self, article):
        template_file = 'agent/articlesummary.template'
        with open(template_file, "r") as file:
            content = file.read()

        for key, value in article.items():
            if value:
                content = content.replace(key, value)

        if self._output:
            with open(self._output, "a") as file:
                file.write(content)
        else:
            print(content)

    def wechat_article_summary(self, url):
        openai_content_max_length = 14000
        doc = self.url2document(url)
        article_image = self.upload_article_image(doc['image'])
        scontent = self.get_suitable_content(doc['content'], openai_content_max_length)
        tags = self.get_content_tags(scontent)
        article_tags = self.generate_linkable_tags(tags)
        article_summary = self.get_content_summary(scontent)
        article = {
            "$ARTICLE_TITLE": doc['title'],
            "$AUTHOR_NAME": doc['author']['name'],
            "$AUTHOR_INTRO": doc['author']['profile']['功能介绍'],
            "$AUTHOR_WECHAT": doc['author']['profile']['微信号'],
            "$ARTICLE_IMAGE": article_image,
            "$ARTICLE_TAGS": article_tags,
            "$ARTICLE_SUMMARY": article_summary,
            "$ARTICLE_ORIGINAL": url,
            "$ARTICLE_WORDS": doc['words'],
            "$ARTICLE_READTIMES": str(math.ceil(int(doc['words']) / 300)) + '分钟',
            #"$ARTICLE_READTIMES": str(int(int(doc['words']) / 300)) + '分钟',
        }
        #print(article)
        self.generate_website_article(article)

    def process_one_record(self, record):
        print("processing record: ", record)
        tlist = re.split('\t', record)
        url = tlist[0]
        self.wechat_article_summary(url)
