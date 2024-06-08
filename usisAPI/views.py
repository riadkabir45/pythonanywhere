from django.http import HttpResponse
from usisLib2 import getCredentials, getRawGrades, getRawTimes, getSession, Semester
# Create your views here.


def getGrade(request,std_id):
    curl = getCredentials("riadkabir45@gmail.com", "21133112Riad@")
    gradeFile =  getRawGrades(curl, std_id)
    response = HttpResponse(gradeFile.getvalue(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename={std_id}.pdf'
    return response


def getTime(request,serv_id,year,session):
    curl = getCredentials("riadkabir45@gmail.com", "21133112Riad@")
    session_id = 0
    for member in Semester:
        if member.name == session:
            session_id = member
    academicSession = getSession(curl,year, session_id)
    gradeFile =  getRawTimes(curl, serv_id, academicSession)
    response = HttpResponse(gradeFile.getvalue(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename={serv_id}.pdf'
    return response
