import os
import re
import sys

from argparse import ArgumentParser
from common.logfd import LogFD
from common.cosclient import COSClient
from common.openai import OpenAIAgent
from agent.similarweb import SimilarwebAgent
from agent.screenshot import ScreenshotAgent
from agent.articlesummary import ArticleSummaryAgent
from pycookiecheat import chrome_cookies

def process_file_lines(fpath, execute_fun, execute_agent):
    rdata_fd = open(fpath, 'r', errors='replace')
    while True:
        lines = rdata_fd.readlines(15000) # characters
        if not lines:
            break

        for line in lines:
            line = line.strip('\n')
            print("processing: ", line)
            result = execute_fun(line)
            #result = execute_fun(execute_agent, line)
            if result == False:
                execute_agent.write_error_log(line)
                continue

    rdata_fd.close()

def init_cos_client(bucket=None, region=None):
    cos_secret_id = os.getenv('COS_SECRET_ID')
    cos_secret_key = os.getenv('COS_SECRET_KEY')
    if cos_secret_id == None or cos_secret_key == None:
        print("Please config COS_SECRET_ID and COS_SECRET_KEY!")
        return None

    if bucket:
        cos_bucket = bucket
    else:
        cos_bucket = os.getenv('COS_BUCKET')
    if region:
        cos_region = region
    else:
        cos_region = os.getenv('COS_REGION')
    #print(cos_secret_id, cos_secret_key, cos_region, cos_bucket)
    return COSClient(cos_secret_id, cos_secret_key, cos_region, cos_bucket)

class Op(object):
    @staticmethod
    def webscreenshot(args):
        try:
            cos_client = init_cos_client(args.cos_bucket, args.cos_region)
            if cos_client == None:
                return -1

            log_fd = LogFD("webscreenshot")
            screenshot_agent = ScreenshotAgent(cos_client, args.cos_prefix, args.output, log_fd,
                                               args.force, args.just_upload_to_cos, args.just_do_ci_process)
            if args.file:
                process_file_lines(args.file, screenshot_agent.process_one_record, screenshot_agent)
            else:
                screenshot_agent.process_one_record(args.inline)
            return 0
        except Exception as e:
            print(e)

    @staticmethod
    def webvisits(args):
        try:
            sweb_url = "https://pro.similarweb.com"
            cookies = chrome_cookies(sweb_url)
            log_fd = LogFD("webvisits")
            similarweb_agent = SimilarwebAgent(sweb_url, cookies, args.output, log_fd)
            if args.file:
                process_file_lines(args.file, similarweb_agent.process_one_record, similarweb_agent)
            else:
                similarweb_agent.process_one_record(args.inline)
            return 0
        except Exception as e:
            print(e)

    @staticmethod
    def articlesummary(args):
        try:
            cos_client = init_cos_client(args.cos_bucket, args.cos_region)
            if cos_client == None:
                return -1

            log_fd = LogFD("articlesummary")
            openai_agent = OpenAIAgent(args.openai_model)
            article_agent = ArticleSummaryAgent(cos_client, args.cos_prefix, openai_agent, args.output, log_fd)
            if args.file:
                process_file_lines(args.file, article_agent.process_one_record, article_agent)
            else:
                article_agent.process_one_record(args.inline)
            return 0
        except Exception as e:
            print(e)

def usage_parser():
    desc = """A command-line tool used to manage xuexiaigc website.
           """
    parser = ArgumentParser(description=desc)
    parser.add_argument('-b', '--cos_bucket', help='Specify COS bucket', default='xuexiaigc-1253766168', type=str)
    parser.add_argument('-r', '--cos_region', help='Specify COS region', default='ap-shanghai', type=str)
    parser.add_argument('-o', '--output', help='Specify output file', default='', type=str)

    file_inline_group = parser.add_mutually_exclusive_group(required=True)
    file_inline_group.add_argument("-f", "--file", default='', type=str, help="use file as input")
    file_inline_group.add_argument("-i", "--inline", default='', type=str, help="use args inline")

    sub_parser = parser.add_subparsers()
    parser_screenshot = sub_parser.add_parser("webscreenshot", help="Generate website screenshot and stored in COS")
    parser_screenshot.add_argument('-p', '--cos-prefix', help='Specify COS object prefix', default='original-screenshot/', type=str, required=False)
    parser_screenshot.add_argument('-f', '--force', help='Force upload screenshot(png) to cos and do CI process', action="store_true", default=False)
    parser_screenshot.add_argument('-u', '--just_upload_to_cos', help='Just upload screenshot(png) to cos', action="store_true", default=False)
    parser_screenshot.add_argument('-c', '--just_do_ci_process', help='Just do ci process to transfer screenshot(png) to regular jpeg', action="store_true", default=False)
    parser_screenshot.set_defaults(func=Op.webscreenshot)

    parser_visits = sub_parser.add_parser("webvisits", help="Get website visits info from pro.similarweb.com, please login in chrome first!")
    parser_visits.set_defaults(func=Op.webvisits)

    parser_articlesummary = sub_parser.add_parser("articlesummary", help="Generate wechat article summary")
    parser_articlesummary.add_argument('-p', '--cos_prefix', help='Specify COS object prefix', default='article-images/', type=str, required=False)
    parser_articlesummary.add_argument('-m', '--openai_model', help='Specify OpenAI model', default='gpt-3.5-turbo-16k-0613', type=str, required=False)
    parser_articlesummary.set_defaults(func=Op.articlesummary)

    args = parser.parse_args()
    print(args)
    return args

# Main entrance
def main(argv):
    args = usage_parser()
    try:
        res = args.func(args)
        return res
    except Exception:
        return 0

if __name__ == '__main__':
    main(sys.argv)

