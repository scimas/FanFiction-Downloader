#!/usr/bin/env python3

import os
import argparse
import requests
from bs4 import BeautifulSoup


def storyExists(sid):
    url = "https://www.fanfiction.net/s/"
    url += str(sid) + "/1/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    errors = soup.find_all("span", attrs={"class": "gui_warning"})
    if len(errors) >= 1:
        return False
    else:
        return True


def chapterExists(sid, chapNum):
    if not storyExists(sid):
        return False

    url = "https://www.fanfiction.net/s/"
    url += str(sid) + "/" + str(chapNum) + "/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    errors = soup.find_all("span", attrs={"class": "gui_normal"})
    for error in errors:
        if "Chapter not found" in error.text:
            return False
    return True


def getChapter(sid, chapNum):
    chapter = ""
    if not chapterExists(sid, chapNum):
        return chapter

    url = "https://www.fanfiction.net/s/"
    url += str(sid) + "/" + str(chapNum) + "/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    rawChapter = soup.find_all("div", attrs={"id": "storytext"})[0]
    for paragraph in rawChapter.find_all("p"):
        chapter += paragraph.text + "\n\n"
    return chapter


def chapterCount(sid):
    count = 0
    if not storyExists(sid):
        return count

    url = "https://www.fanfiction.net/s/"
    url += str(sid) + "/1/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    info = soup.find_all("span", attrs={"class": "xgray xcontrast_txt"})[0]
    info = info.text
    count = info[info.find("Chapters: ") + 10 : info.find("- Words")]
    count = int(count.strip())
    return count


def saveStory(sid):
    if not storyExists(sid):
        print("Story doesn't exist")
        return False

    url = "https://www.fanfiction.net/s/"
    url += str(sid) + "/1/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    title = soup.find_all("title")[0].text
    title = title[:title.find("Chapter") - 1]
    if not os.path.exists(title):
        os.mkdir(title)
    elif not os.path.isdir(title):
        print("Can't save the story.")
        print("A file with the story name already exists in this directory.")
        print("Change that file's name or move to another directory and retry.")
        return False

    for num in range(1, chapterCount(sid) + 1):
        chapter = getChapter(sid, num)
        with open(title + "/Chapter " + str(num) + ".txt", "w") as f:
            f.write(chapter)

    print("Story has been saved in a directory named " + title)


def saveChapter(sid, chapNum):
    if not chapterExists(sid, chapNum):
        print("Story or chapter doesn't exist")
        return False

    url = "https://www.fanfiction.net/s/"
    url += str(sid) + "/1/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    title = soup.find_all("title")[0].text
    title = title[:title.find("Chapter") - 1]
    if not os.path.exists(title):
        os.mkdir(title)
    elif not os.path.isdir(title):
        print("Can't save the chapter.")
        print("A file with the story name already exists in this directory.")
        print("Change that file's name or move to another directory and retry.")
        return False

    chapter = getChapter(sid, chapNum)
    with open(title + "/Chapter " + str(chapNum) + ".txt", "w")  as f:
        f.write(chapter)

    print("Chapter has been saved in a directory named " + title)


parser = argparse.ArgumentParser(description="Download stories from FanFiction.net")
parser.add_argument("story_id",
                    type=int,
                    help="Id of the story. (fanfiction.net/s/<story_id>/")
parser.add_argument("-c", "--chapter",
                    type=int,
                    help="Number of the chapter to download")

args = parser.parse_args()

if args.chapter:
    saveChapter(args.story_id, args.chapter)
else:
    saveStory(args.story_id)
