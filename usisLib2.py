from requests import Session as Downloader
from io import BytesIO as RawFile
from enum import Enum
from re import search as RegSearch

from PyPDF2 import PdfReader as PdfScrap
from tabula import read_pdf as PdfTableScrap


class UsisInvalidUser(Exception):
    "Raised when user or pass is incorrect"
    pass


class UsisExpiredSession(Exception):
    "Raised when user session expired"
    pass


class UsisInvalidStudent(Exception):
    "Raised when student dont exist"
    pass


class Semester(Enum):
    Spring = 0
    Summer = 1
    Fall = 2


def defaultRegex(patern, txt, defaultValue=None):
    out = RegSearch(patern, txt)
    if out is None:
        return defaultValue
    else:
        return out.group()


def getCredentials(user, passwd):
    dataDownloader = Downloader()
    dataDownloader.get("https://usis.bracu.ac.bd/academia")
    response = dataDownloader.post(
        "https://usis.bracu.ac.bd/academia/j_spring_security_check",
        data={"j_username": user, "j_password": passwd},
    )
    if (
        response.url == "https://usis.bracu.ac.bd"
        "/academia/login/authfail?login_error=1"
    ):
        raise UsisInvalidUser("Invalid Credintials")
    return dataDownloader


def getSession(downloader, year, semester):
    url = (
        "https://usis.bracu.ac.bd/academia/academiaSession/"
        f"getAllSessionByYear?year={year}"
    )
    sessionData = downloader.get(url).json()
    for index in range(3):
        if sessionData[index]["title"].split()[0] == semester.name:
            return sessionData[index]["id"]
    return -1


def getRawTimes(dataDownloader, serverID, sessionTime):
    url = (
        "https://usis.bracu.ac.bd/academia/studentCourse"
        "/createSchedulePDF?content=pdf&studentId="
        f"{str(serverID)}"
        f"&sessionId={str(sessionTime)}"
    )
    rawData = dataDownloader.get(url)
    if rawData.url == "https://usis.bracu.ac.bd/academia/":
        raise UsisExpiredSession("User Session Expired")
    if rawData.status_code == 500:
        raise UsisInvalidStudent("Student data not found")
    memFile = RawFile()
    memFile.write(rawData.content)
    return memFile


def getBasicInfo(tFile):
    text = PdfScrap(tFile).pages[0].extract_text()
    nm = defaultRegex("Name : .+", text, "xxxxxxxNULL")[7:]
    pg = defaultRegex("Program: [A-Z]+", text, "xxxxxxxxxNULL")[9:]
    uid = defaultRegex("ID : [0-9]+", text, "xxxxxNULL")[5:]
    return (nm, pg, uid)


def parseTimes(tFile):
    times = []
    times.extend(getBasicInfo(tFile))

    datasheet = PdfTableScrap(tFile, pages=1, silent=True)[0]
    # import pdb; pdb.set_trace()
    print(datasheet)
    for index in datasheet:
        if index == "Time/Day":
            continue
        for i in range(len(datasheet[index])):
            data = str(datasheet[index][i])
            if data == "nan":
                continue
            data = data.replace("\r", " ")
            time = str(datasheet["Time/Day"][i]).replace("\r", "")
            times.append(index[:3] + "(" + time + " - " + data + ")")
    return times


def getRawGrades(dataDownloader, studentID):
    checkID = 22141006
    url = (
        "https://usis.bracu.ac.bd/academia/studentGrade/"
        + "rptStudentGradeSheetByStudent?reportFormat=PDF&studentId="
        + str(checkID)
    )
    originData = dataDownloader.get(url)
    if originData.url == "https://usis.bracu.ac.bd/academia/":
        raise UsisExpiredSession("User Session Expired")
    gradeUrl = originData.url.replace("=22141006&", "=" + str(studentID) + "&")
    rawData = dataDownloader.get(gradeUrl)
    if len(rawData.content) == 48473:
        raise UsisInvalidUser("Student data not found")
    memFile = RawFile()
    memFile.write(rawData.content)
    return memFile
