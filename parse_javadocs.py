import os
import re
from bs4 import BeautifulSoup
import pandas as pd

from log_utils import ColoredLogger

logger = ColoredLogger("parser")

JAVADOC_DIR = os.path.expanduser("~/JavaDocScraper/JavaDocs")
OUTPUT_DIR = os.path.expanduser("~/JavaDocScraper/")

def parse_class_list(directory):
    classes, methods = [], []
    all_classes_html = os.path.join(directory, "allclasses-frame.html")
    soup = BeautifulSoup(open(all_classes_html, 'r').read(), 'html.parser')
    filtered = soup.find_all('a')
    for element in filtered:
        class_dir = os.path.join(directory, element['href'])
        c, ms = single_class(class_dir)
        classes.append(c)
        methods.extend(ms)
    return classes, methods

def single_class(directory):
    logger.debug(directory)
    class_ = {}
    class_["url"] = "/".join(os.path.dirname(directory).split("/")[-2:])
    soup = BeautifulSoup(open(directory, 'r').read(), 'html.parser')

    # API name
    api = soup.find("div", {"class": "subTitle"}).get_text()
    class_["api"] = api

    # Class name
    class_name = soup.find("h2", {"class": "title"}).get_text()
    logger.debug(class_name)
    class_["class"] = class_name

    # Class description
    class_description_block = soup.find(
        "div", {"class": "description"}).find("div", {"class": "block"})
    if class_description_block:
        if class_description_block.find("h1"):
            class_description_block.find("h1").clear()
        class_description = re.sub(
            ' +', ' ', class_description_block.get_text().strip().replace('\n', ''))
        logger.debug(class_description)
        class_["description"] = class_description

    logger.debug("-Methods-")
    # Method details
    methods = []
    details = soup.find("div", {"class": "details"})
    if details:
        details = details.find("li", {"class": "blockList"}).find_all(
            "ul", {"class": "blockList"})
        for d in details:
            for ul_block in d.find_all("ul", {"class": "blockList"}):
                method_signature = re.sub(
                    ' +', ' ', ul_block.find("pre").get_text().strip().replace('\n', ''))
                method_description_block = ul_block.find(
                    "div", {"class": "block"})
                method = {}
                method["url"] = "/".join(os.path.dirname(directory).split("/")[-2:])
                method["api"] = api
                method["class"] = class_name
                method["method"] = method_signature
                logger.debug(method_signature)
                if method_description_block:
                    method_description = re.sub(
                        ' +', ' ', method_description_block.get_text().replace('\n', ''))
                    method["description"] = method_description.replace(
                        '"', '')
                    logger.debug(method_description)
                methods.append(method)
                logger.debug("---")
    logger.debug("-----END OF CLASS------\n")
    return class_, methods


def parse_java_docs():
    class_descriptions = []
    method_descriptions = []

    for folder in os.listdir(JAVADOC_DIR):
        if os.path.isdir(os.path.join(JAVADOC_DIR, folder)):
            for sub_folder in os.listdir(os.path.join(JAVADOC_DIR, folder)):
                directory = os.path.join(JAVADOC_DIR, folder, sub_folder)
                logger.debug("Directory {}".format(directory))
                if os.path.isdir(directory):
                    # Parse JavaDoc Content
                    try:
                        cls_descs, mtd_descs = parse_class_list(directory)
                        class_descriptions.extend(cls_descs)
                        method_descriptions.extend(mtd_descs)
                    except FileNotFoundError:
                        logger.error("File not found {}".format(directory))
                    except AttributeError as error:
                        logger.error(error)
                    except Exception as error:
                        logger.error(error)
    class_ = pd.DataFrame(class_descriptions)
    method_ = pd.DataFrame(method_descriptions)
    class_.to_csv(os.path.join(OUTPUT_DIR, "classes.csv"))
    method_.to_csv(os.path.join(OUTPUT_DIR, "methods.csv"))


if __name__ == "__main__":
    parse_java_docs()
