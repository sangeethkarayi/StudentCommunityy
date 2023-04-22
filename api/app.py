from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api, abort, reqparse
from flask_cors import CORS
import werkzeug
from firebase import Firebase
from datetime import datetime
from pytz import timezone

DOWNLOAD_DIRECTORY = "static/downloads"

app = Flask(__name__)
api = Api(app)
CORS(app)

config = {
  "apiKey": "AIzaSyB1JFBD-wDv5fdrCfqBopVf1EqvBEgXvvY",
  "authDomain": "studentcommunity2023",
  "databaseURL": "https://studentcommunity2023-default-rtdb.firebaseio.com",
  "storageBucket": "studentcommunity2023.appspot.com"
}
config_admin = {
  "apiKey": "AIzaSyCwpZAGJgBRdYpuYxD7OhhJr991uQcEEKc",
  "authDomain": "database-9c6e7.firebaseapp.com",
  "databaseURL": "https://database-9c6e7-default-rtdb.firebaseio.com",
  "storageBucket": "database-9c6e7.appspot.com"
}

firebase=Firebase(config)
db=firebase.database()
storage = firebase.storage()

firebase_admin=Firebase(config)
db_admin=firebase_admin.database()

childName = 'StudentCommunity'

studentRegParser=reqparse.RequestParser()
studentRegParser.add_argument('name', type=str, required=True)
studentRegParser.add_argument('gender', type=str, required=True)
studentRegParser.add_argument('dob', type=str, required=True)
studentRegParser.add_argument('courseID', type=str, required=True)
studentRegParser.add_argument('college', type=str, required=True)
studentRegParser.add_argument('email', type=str, required=True)
studentRegParser.add_argument('password', type=str, required=True)
studentRegParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files', required=True)

studentUpdateParser=reqparse.RequestParser()
studentUpdateParser.add_argument('name', type=str)
studentUpdateParser.add_argument('gender', type=str)
studentUpdateParser.add_argument('dob', type=str)
studentUpdateParser.add_argument('courseID', type=str)
studentUpdateParser.add_argument('college', type=str)
studentUpdateParser.add_argument('email', type=str)
studentUpdateParser.add_argument('password', type=str)
studentUpdateParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')

loginParser=reqparse.RequestParser()
loginParser.add_argument('cat', type=str, required=True)
loginParser.add_argument('username', type=str, required=True)
loginParser.add_argument('password', type=str, required=True)

courseRegParser=reqparse.RequestParser()
courseRegParser.add_argument('name' , type=str , required=True)

noteRegParser=reqparse.RequestParser()
noteRegParser.add_argument('studentID', type=str, required=True)
noteRegParser.add_argument('courseID', type=str, required=True)
noteRegParser.add_argument('subjectName', type=str, required=True)
noteRegParser.add_argument('description', type=str, required=True)
noteRegParser.add_argument('doc', type=werkzeug.datastructures.FileStorage, location='files', action='append', required=True)

noteUpdateParser=reqparse.RequestParser()
noteUpdateParser.add_argument('subjectName', type=str, required=True)
noteUpdateParser.add_argument('description', type=str, required=True)

noteDocUpdateParser = reqparse.RequestParser()
noteDocUpdateParser.add_argument('doc', type=werkzeug.datastructures.FileStorage, location='files', action='append')
noteDocUpdateParser.add_argument('fname', type=str)

noteActionParser=reqparse.RequestParser()
noteActionParser.add_argument('noteID', type=str, required=True)
noteActionParser.add_argument('action', type=str, required=True)

communityPostParser=reqparse.RequestParser()
communityPostParser.add_argument('courseID', type=str, required=True)
communityPostParser.add_argument('post', type=str, required=True)
communityPostParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')

communityPostUpdateParser=reqparse.RequestParser()
communityPostUpdateParser.add_argument('post', type=str)
communityPostUpdateParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')

postCommentParser = reqparse.RequestParser()
postCommentParser.add_argument('studentID', type=str, required=True)
postCommentParser.add_argument('comment', type=str, required=True)

postCommentUpdateParser = reqparse.RequestParser()
postCommentUpdateParser.add_argument('comment', type=str, required=True)

noteCommentParser = reqparse.RequestParser()
noteCommentParser.add_argument('studentID', type=str, required=True)
noteCommentParser.add_argument('comment', type=str, required=True)

noteCommentUpdateParser = reqparse.RequestParser()
noteCommentUpdateParser.add_argument('comment', type=str, required=True)

noteRatingParser = reqparse.RequestParser()
noteRatingParser.add_argument('studentID', type=str, required=True)
noteRatingParser.add_argument('rating', type=int, required=True)

filterItemListparser=reqparse.RequestParser()
filterItemListparser.add_argument('studentID', type=str, required=True)

filterParser=reqparse.RequestParser()
filterParser.add_argument('studentID', type=str, required=True)
filterParser.add_argument('cat', type=str, required=True)
filterParser.add_argument('item', type=str, required=True)

class StudentReg(Resource):
  def post(self):
    args=studentRegParser.parse_args()
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
    if not args['courseID'] in courseList:
      abort(400, message='course not found')
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    flag = 0
    for i in studentList:
      if studentList[i]['email'] == args['email']:
        flag = 1
    if flag == 1:
      abort(400, message='email id already used')
    studentCnt = db.child(childName).child('studentCnt').get().val()
    if studentCnt == None:
      studentCnt = 0
    studentCnt += 1
    studentID = 'STUD' + str(studentCnt + 100)
    db.child(childName).child('studentCnt').set(studentCnt)
    fname = studentID + '.jpg'
    f = args['photo']
    del args['photo']
    storage.child(childName).child('studentImage').child(fname).put(f)
    args['imgUrl'] = storage.child(childName).child('studentImage').child(fname).get_url(None)
    studentList[studentID] = args
    db.child(childName).child('studentList').set(studentList)
    return studentList

class StudentUpdate(Resource):
  def get(self, studentID):
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
    if not studentID in studentList:
      abort(400, message='student not found')
    else:
      studentDetails = studentList[studentID]
      studentDetails['courseDetails'] = courseList[studentDetails['courseID']]
      return studentDetails

  def put(self, studentID):
    args=studentUpdateParser.parse_args()
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if not studentID in studentList:
      abort(400, message='student not found')
    if args['name']:
      studentList[studentID]['name'] = args['name']
    if args['gender']:
      studentList[studentID]['gender'] = args['gender']
    if args['dob']:
      studentList[studentID]['dob'] = args['dob']
    if args['college']:
      studentList[studentID]['college'] = args['college']
    if args['email']:
      studentList[studentID]['email'] = args['email']
    if args['photo']:
      fname = studentID + '.jpg'
      storage.child(childName).child('studentImage').child(fname).put(args['photo'])
      studentList[studentID]['imgUrl'] = storage.child(childName).child('studentImage').child(fname).get_url(None)
    if args['courseID']:
      courseList=db.child(childName).child('courseList').get().val()
      if courseList==None:
        courseList={'COURSEOTH' : {'name' : 'others'}}
      if args['courseID'] in courseList:
        studentList[studentID]['courseID'] = args['courseID']
      else:
        abort(400, message='course not found')
    db.child(childName).child('studentList').set(studentList)
    return studentList[studentID]

class StudentList(Resource):
  def get(self, courseID):
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
    if courseID not in courseList:
      abort(400, message='course not found')
    tempStudentList = {}
    for i in studentList:
      if studentList[i]['courseID'] == courseID:
        tempStudentList[i] = studentList[i]
    return tempStudentList

class Login(Resource):
  def post(self):
    args=loginParser.parse_args()
    loginID = ''
    if args['cat'] == 'student':
      studentList = db.child(childName).child('studentList').get().val()
      if studentList == None:
          studentList = {}
      for i in studentList:
        if studentList[i]['email'] == args['username'] and studentList[i]['password'] == args['password']:
          loginID = i
          break
    elif args['cat'] == 'admin':
      adminEmail = db_admin.child(childName).child('adminEmail').get().val()
      if adminEmail == None:
          adminEmail = 'admin@gmail.com'
          db_admin.child(childName).child('adminEmail').set(adminEmail)
      adminPassword = db_admin.child(childName).child('adminPassword').get().val()
      if adminPassword == None:
          adminPassword = 'admin123'
          db_admin.child(childName).child('adminPassword').set(adminPassword)
      if adminEmail == args['username'] and adminPassword == args['password']:
        loginID = 'admin'
    else:
      abort(400, message='invalid category')
    return loginID

class CourseReg(Resource):
  def post(self):
    args= courseRegParser.parse_args()
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    flag = 0
    for i in courseList:
      if args['name'].lower() == courseList[i]['name'].lower():
        flag = 1
        break
    if flag == 1:
      abort(400, message='course already registered')
    courseCnt=db.child(childName).child('courseCnt').get().val()
    if courseCnt==None:
      courseCnt=0
    courseCnt+=1
    db.child(childName).child('courseCnt').set(courseCnt)
    courseID= 'COURSE' + str(100+courseCnt)
    courseList[courseID]=args
    db.child(childName).child('courseList').set(courseList)
    return courseList

  def get(self):
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    return courseList

class CourseUpdate(Resource):
  def delete(self,courseID):
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    studentList=db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if courseID in courseList:
      flag = 0
      for i in studentList:
        if studentList[i]['courseID'] == courseID: 
          flag = 1
          break
      if flag == 0:
        del courseList[courseID]
      elif flag == 1:
        abort(400, message='course found in student list')
    else:
      abort(400,message='course not found')
    db.child(childName).child('courseList').set(courseList)
    return courseList

  def put(self,courseID):
    args= courseRegParser.parse_args()
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    if courseID in courseList:
      for i in courseList:
        if i != courseID and courseList[i]['name'].lower() == args['name'].lower():
          abort(400, message='course name already used')
      courseList[courseID]['name']=args['name']
      db.child(childName).child('courseList').set(courseList)
    else:
      abort(400,message='course not found')
    return courseList

class NoteReg(Resource):
  def post(self):
    args=noteRegParser.parse_args()
    docs=args['doc']
    del args['doc']
    studentList=db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    if not args['studentID'] in studentList:
      abort(400, message='student not found')
    if not args['courseID'] in courseList:
      abort(400, message='course not found')
    if studentList[args['studentID']]['courseID'] != args['courseID']:
      abort(400, message='not student course')
    args['docList']=[]
    for i in docs:
      docCnt=db.child(childName).child('docCnt').get().val()
      if docCnt==None:
        docCnt=0
      docCnt+=1
      db.child(childName).child('docCnt').set(docCnt)
      fname = 'DOC' + str(docCnt+100) + '.' + i.filename.rsplit('.', 1)[1]
      storage.child(childName).child('docs').child(fname).put(i)
      docUrl=storage.child(childName).child('docs').child(fname).get_url(None)
      args['docList'].append({'fname':fname,'docUrl':docUrl})
    noteCnt=db.child(childName).child('noteCnt').get().val()
    if noteCnt==None:
      noteCnt=0
    noteCnt+=1
    db.child(childName).child('noteCnt').set(noteCnt)
    noteID= 'NOTE' + str(100+noteCnt)
    noteList=db.child(childName).child('noteList').get().val()
    if noteList==None:
      noteList={}
    noteList[noteID]=args
    noteList[noteID]['totalRating'] = 0
    noteList[noteID]['totalRatedStudents'] = 0
    noteList[noteID]['status'] = 'notApproved'
    x = datetime.now(timezone("Asia/Kolkata"))
    noteList[noteID]['date'] = x.strftime('%d/%m/%Y')
    noteList[noteID]['time'] = x.strftime('%X')
    db.child(childName).child('noteList').set(noteList)
    return noteList

  def get(self):
    studentList=db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    noteList=db.child(childName).child('noteList').get().val()
    if noteList==None:
      noteList={}
    approvedNoteList = {}
    notApprovedNoteList = {}
    blockedNoteList ={}
    for i in noteList:
      if 'totalRatedStudents' not in noteList[i]:
        noteList[i]['totalRatedStudents'] = 0
      if 'totalRating' not in noteList[i]:
        noteList[i]['totalRating'] = 0
      if noteList[i]['totalRatedStudents'] > 0:
        noteList[i]['averageRating'] = round(noteList[i]['totalRating']/noteList[i]['totalRatedStudents'])
      else:
        noteList[i]['averageRating'] = 0
      if noteList[i]['status'] == 'notApproved':
        notApprovedNoteList[i] = noteList[i]
        notApprovedNoteList[i]['studentDetails'] = studentList[notApprovedNoteList[i]['studentID']]
        notApprovedNoteList[i]['courseDetails'] = courseList[notApprovedNoteList[i]['courseID']]
      elif noteList[i]['status'] == 'approved':
        approvedNoteList[i] = noteList[i]
        approvedNoteList[i]['studentDetails'] = studentList[approvedNoteList[i]['studentID']]
        approvedNoteList[i]['courseDetails'] = courseList[approvedNoteList[i]['courseID']]
      elif noteList[i]['status'] == 'blocked':
        blockedNoteList[i] = noteList[i]
        blockedNoteList[i]['studentDetails'] = studentList[blockedNoteList[i]['studentID']]
        blockedNoteList[i]['courseDetails'] = courseList[blockedNoteList[i]['courseID']]
    noteDict = {
      'notApproved' : notApprovedNoteList,
      'approved'    : approvedNoteList,
      'blocked'     : blockedNoteList
    }
    return noteDict

class NoteUpdate(Resource):
  def get(self, noteID):
    studentList=db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    noteList=db.child(childName).child('noteList').get().val()
    if noteList==None:
      noteList={}
    noteDetails = noteList[noteID]
    if 'totalRatedStudents' not in noteDetails:
      noteDetails['totalRatedStudents'] = 0
    if 'totalRating' not in noteDetails:
      noteDetails['totalRating'] = 0
    if noteDetails['totalRatedStudents'] > 0:
      noteDetails['averageRating'] = round(noteDetails['totalRating']/noteDetails['totalRatedStudents'])
    else:
      noteDetails['averageRating'] = 0
    noteDetails['studentDetails'] = studentList[noteDetails['studentID']]
    noteDetails['courseDetails'] = courseList[noteDetails['courseID']]
    noteDetails['studentDetails']['courseDetails'] = courseList[studentList[noteDetails['studentID']]['courseID']]
    if 'totalRatedStudents' not in noteDetails:
      noteDetails['totalRatedStudents'] = 0
    if 'totalRating' not in noteDetails:
      noteDetails['totalRating'] = 0
    if noteDetails['totalRatedStudents'] > 0:
      noteDetails['averageRating'] = round(noteDetails['totalRating']/noteDetails['totalRatedStudents'])
    else:
      noteDetails['averageRating'] = 0
    return noteDetails

  def put(self, noteID):
    args = noteUpdateParser.parse_args()
    noteList = db.child(childName).child('noteList').get().val()
    if noteList == None:
      noteList = {}
    if noteID in noteList:
        if args['subjectName']:
          noteList[noteID]['subjectName'] = args['subjectName']
        if args['description']:
          noteList[noteID]['description'] = args['description']
        db.child(childName).child('noteList').set(noteList)
        noteDetails= noteList[noteID]
    else:
      abort(400, message='note not found')
    return noteDetails

class NoteDocUpdate(Resource):
  def put(self,noteID):
    args = noteDocUpdateParser.parse_args()
    if args['photo']:
      noteList = db.child(childName).child('noteList').get().val()
      if noteList == None:
        noteList = {}
      if noteID in noteList:
        docs = args['doc']
        for i in docs:
          docCnt = db.child(childName).child('docCnt').get().val()
          if docCnt == None:
            docCnt = 0
          docCnt += 1
          db.child(childName).child('docCnt').set(docCnt)
          fname = 'DOC' + str(100 + docCnt) + i.filename.rsplit('.', 1)[1]
          storage.child(childName).child('docs').child(fname).put(i)
          docUrl = storage.child(childName).child('docs').child(fname).get_url(None)
          noteList[noteID]['docList'].append({'fname' : fname, 'docUrl' : docUrl})
        db.child(childName).child('noteList').set(noteList)
      else:
        abort(400, message='note not found')
    else:
      abort(400, message='photo required')
    return noteList[noteID]

  def delete(self,noteID):
    noteList = db.child(childName).child('noteList').get().val()
    if noteList == None:
      noteList = {}
    args = noteDocUpdateParser.parse_args()
    if args['fname']:
      if noteID in noteList:
        if len(noteList[noteID]['docList']) > 1:
          flag = 0
          for i in noteList[noteID]['imgList']:
            if i['fname'] == args['fname']:
              flag = 1
              noteList[noteID]['docList'].remove(i)
              db.child(childName).child('noteList').set(noteList)
          if flag == 0:
            abort(400, message='doc not found')
        else:
          abort(400, message='minimum one doc required')
      else:
        abort(400, message='note not found')
    else:
      abort(400, message='documnet name required')
    return noteList[noteID]

class StudentNotes(Resource):
  def get(self, studentID):
    studentList=db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    noteList=db.child(childName).child('noteList').get().val()
    if noteList==None:
      noteList={}
    if studentID != 'nil':
      if not studentID in studentList:
        abort(400, message='student not found')
    allNoteList = {}
    approvedNoteList = {}
    notApprovedNoteList = {}
    blockedNoteList ={}
    othNoteList = {}
    for i in noteList:
      if 'totalRatedStudents' not in noteList[i]:
        noteList[i]['totalRatedStudents'] = 0
      if 'totalRating' not in noteList[i]:
        noteList[i]['totalRating'] = 0
      if noteList[i]['totalRatedStudents'] > 0:
        noteList[i]['averageRating'] = round(noteList[i]['totalRating']/noteList[i]['totalRatedStudents'])
      else:
        noteList[i]['averageRating'] = 0
      if noteList[i]['status'] == 'approved':
        allNoteList[i] = noteList[i]
        allNoteList[i]['studentDetails'] = studentList[allNoteList[i]['studentID']]
        allNoteList[i]['courseDetails'] = courseList[allNoteList[i]['courseID']]
        if studentID != 'nil':
          if noteList[i]['studentID'] != studentID and noteList[i]['courseID'] == studentList[studentID]['courseID']:
            othNoteList[i] = noteList[i]
            othNoteList[i]['studentDetails'] = studentList[othNoteList[i]['studentID']]
            othNoteList[i]['courseDetails'] = courseList[othNoteList[i]['courseID']]
      if noteList[i]['studentID'] == studentID:
        if noteList[i]['status'] == 'notApproved':
          notApprovedNoteList[i] = noteList[i]
          notApprovedNoteList[i]['studentDetails'] = studentList[notApprovedNoteList[i]['studentID']]
          notApprovedNoteList[i]['courseDetails'] = courseList[notApprovedNoteList[i]['courseID']]
        elif noteList[i]['status'] == 'approved':
          approvedNoteList[i] = noteList[i]
          approvedNoteList[i]['studentDetails'] = studentList[approvedNoteList[i]['studentID']]
          approvedNoteList[i]['courseDetails'] = courseList[approvedNoteList[i]['courseID']]
        elif noteList[i]['status'] == 'blocked':
          blockedNoteList[i] = noteList[i]
          blockedNoteList[i]['studentDetails'] = studentList[blockedNoteList[i]['studentID']]
          blockedNoteList[i]['courseDetails'] = courseList[blockedNoteList[i]['courseID']]
    noteDict = {
      'all'         : allNoteList,
      'notApproved' : notApprovedNoteList,
      'approved'    : approvedNoteList,
      'blocked'     : blockedNoteList,
      'others'      : othNoteList
    }
    return noteDict

class DownloadFile(Resource):
  def get(self, fname):
    noteList=db.child(childName).child('noteList').get().val()
    if noteList==None:
      noteList={}
    for i in noteList:
      for j in noteList[i]['docList']:
        if j['fname'] == fname:
          storage.child(childName).child('docs').child(fname).download(DOWNLOAD_DIRECTORY + '/' + fname)
          return send_from_directory(DOWNLOAD_DIRECTORY, fname, as_attachment=True)

class NoteAction(Resource):
  def post(self):
    args=noteActionParser.parse_args()
    noteList = db.child(childName).child('noteList').get().val()
    if noteList == None:
      noteList = {}
    if args['noteID'] in noteList:
      if args['action'] == 'approve':
        if noteList[args['noteID']]['status'] == 'notApproved':
          noteList[args['noteID']]['status'] = 'approved'
        else:
          abort(400, message='cant be approved')
      elif args['action'] == 'block':
        if noteList[args['noteID']]['status'] == 'approved':
          noteList[args['noteID']]['status'] = 'blocked'
        else:
          abort(400, message='cant be blocked')
      elif args['action'] == 'unblock':
        if noteList[args['noteID']]['status'] == 'blocked':
          noteList[args['noteID']]['status'] = 'approved'
        else:
          abort(400, message='cant be unblocked')
      else:
        abort(400, message='invalid action')
      db.child(childName).child('noteList').set(noteList)
    else:
      abort(400, message='note not found')

class CommunityPost(Resource):
  def post(self, studentID):
    args=communityPostParser.parse_args()
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if args['courseID'] not in courseList:
      abort(400, message='course not found')
    if studentID not in studentList:
      abort(400, message='student not found')
    postCnt = db.child(childName).child('postCnt').get().val()
    if postCnt == None:
      postCnt = 0
    postCnt += 1
    postID = 'POST' + str(postCnt + 100)
    db.child(childName).child('postCnt').set(postCnt)
    if args['photo']:
      fname = postID + '.jpg'
      f = args['photo']
      del args['photo']
      storage.child(childName).child('postImage').child(fname).put(f)
      args['imgUrl'] = storage.child(childName).child('postImage').child(fname).get_url(None)
    else:
      args['imgUrl'] = ''
    postList = db.child(childName).child('postList').get().val()
    if postList == None:
      postList = {}
    postList[postID] = args
    x = datetime.now(timezone("Asia/Kolkata"))
    postList[postID]['date'] = x.strftime('%d/%m/%Y')
    postList[postID]['time'] = x.strftime('%X')
    postList[postID]['studentID'] = studentID
    db.child(childName).child('postList').set(postList)
    return postList

  def get(self, studentID):
    postList = db.child(childName).child('postList').get().val()
    if postList == None:
      postList = {}
    keyList = list(postList.keys())
    keyList.reverse()
    tempPostList = {}
    for i in keyList:
      tempPostList[i] = postList[i]
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if studentID not in studentList:
      abort(400, message='student not found')
    myPost = {}
    otherPost = {}
    for i in tempPostList:
      if tempPostList[i]['studentID'] == studentID:
        myPost[i] = tempPostList[i]
      elif tempPostList[i]['courseID'] == studentList[studentID]['courseID']:
        otherPost[i] = tempPostList[i]
        otherPost[i]['studentDetails'] = studentList[otherPost[i]['studentID']]
    postDict = { 'myPost' : myPost, 'otherPost' : otherPost }
    return postDict

class CommunityPostUpdate(Resource):
  def delete(self, postID):
    postList = db.child(childName).child('postList').get().val()
    if postList == None:
      postList = {}
    if postID not in postList:
      abort(400, message='post not found')
    del postList[postID]
    db.child(childName).child('postList').set(postList)
    return postList

  def put(self, postID):
    args=communityPostUpdateParser.parse_args()
    postList = db.child(childName).child('postList').get().val()
    if postList == None:
      postList = {}
    if postID not in postList:
      abort(400, message='post not found')
    if args['post']:
      postList[postID]['post'] = args['post']
    if args['photo']:
      fname = postID + '.jpg'
      storage.child(childName).child('postImage').child(fname).put(args['photo'])
      postList[postID]['imgUrl'] = storage.child(childName).child('postImage').child(fname).get_url(None)
    db.child(childName).child('postList').set(postList)
    return postList[postID]

  def get(self, postID):
    postList = db.child(childName).child('postList').get().val()
    if postList == None:
      postList = {}
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if postID not in postList:
      abort(400, message='post not found')
    postDetails = postList[postID]
    postDetails['studentDetails'] = studentList[postDetails['studentID']]
    return postDetails

class PostComment(Resource):
  def post(self, postID):
    args = postCommentParser.parse_args()
    studentID = args['studentID']
    comment = args['comment']
    postList = db.child(childName).child('postList').get().val()
    if postList == None:
      postList = {}
    if not postID in postList:
      abort(400, message='post not found')
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if not studentID in studentList:
      abort(400, message='student not found')
    commentCnt = db.child(childName).child('commentCnt').get().val()
    if commentCnt == None:
      commentCnt = 0
    commentCnt += 1
    db.child(childName).child('commentCnt').set(commentCnt)
    commentID = 'CMNT' + str(100 + commentCnt)
    postCommentList = db.child(childName).child('postCommentList').get().val()
    if postCommentList == None:
      postCommentList = {}
    x = datetime.now(timezone("Asia/Kolkata"))
    date = x.strftime('%d/%m/%Y')
    time = x.strftime('%X')
    postCommentList[commentID] = {
      'postID'    : postID,
      'studentID' : studentID,
      'comment'   : comment,
      'date'      : date,
      'time'      : time
    }
    db.child(childName).child('postCommentList').set(postCommentList)
    return postCommentList[commentID]

  def get(self, postID):
    postList = db.child(childName).child('postList').get().val()
    if postList == None:
      postList = {}
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if not postID in postList:
      abort(400, message='post not found')
    postCommentList = db.child(childName).child('postCommentList').get().val()
    if postCommentList == None:
      postCommentList = {}
    tempCommentList = {}
    for i in postCommentList:
      if postCommentList[i]['postID'] == postID:
        tempCommentList[i] = postCommentList[i]
        tempCommentList[i]['studentDetails'] = studentList[postCommentList[i]['studentID']]
    return tempCommentList

class PostCommentUpdate(Resource):
  def put(self, commentID):
    commentID = commentID.upper()
    args = postCommentUpdateParser.parse_args()
    postCommentList = db.child(childName).child('postCommentList').get().val()
    if postCommentList == None:
      postCommentList = {}
    if commentID in postCommentList:
      postCommentList[commentID]['comment'] = args['comment']
      db.child(childName).child('postCommentList').set(postCommentList)
      commentDetails= postCommentList[commentID]
    else:
      abort(400, message='comment not found')
    return commentDetails

  def delete(self, commentID):
    commentID = commentID.upper()
    postCommentList = db.child(childName).child('postCommentList').get().val()
    if postCommentList == None:
      postCommentList = {}
    if commentID in postCommentList:
        del postCommentList[commentID]
        db.child(childName).child('postCommentList').set(postCommentList)
    else:
      abort(400, message='comment not found')
    return postCommentList

class NoteComment(Resource):
  def post(self, noteID):
    args = noteCommentParser.parse_args()
    studentID = args['studentID']
    comment = args['comment']
    noteList = db.child(childName).child('noteList').get().val()
    if noteList == None:
      noteList = {}
    if not noteID in noteList:
      abort(400, message='note not found')
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if not studentID in studentList:
      abort(400, message='student not found')
    commentCnt = db.child(childName).child('commentCnt').get().val()
    if commentCnt == None:
      commentCnt = 0
    commentCnt += 1
    db.child(childName).child('commentCnt').set(commentCnt)
    commentID = 'CMNT' + str(100 + commentCnt)
    noteCommentList = db.child(childName).child('noteCommentList').get().val()
    if noteCommentList == None:
      noteCommentList = {}
    x = datetime.now(timezone("Asia/Kolkata"))
    date = x.strftime('%d/%m/%Y')
    time = x.strftime('%X')
    noteCommentList[commentID] = {
      'noteID'    : noteID,
      'studentID' : studentID,
      'comment'   : comment,
      'date'      : date,
      'time'      : time
    }
    db.child(childName).child('noteCommentList').set(noteCommentList)
    return noteCommentList[commentID]

  def get(self, noteID):
    noteList = db.child(childName).child('noteList').get().val()
    if noteList == None:
      noteList = {}
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if not noteID in noteList:
      abort(400, message='note not found')
    noteCommentList = db.child(childName).child('noteCommentList').get().val()
    if noteCommentList == None:
      noteCommentList = {}
    tempCommentList = {}
    for i in noteCommentList:
      if noteCommentList[i]['noteID'] == noteID:
        tempCommentList[i] = noteCommentList[i]
        tempCommentList[i]['studentDetails'] = studentList[noteCommentList[i]['studentID']]
    return tempCommentList

class NoteCommentUpdate(Resource):
  def put(self, commentID):
    commentID = commentID.upper()
    args = noteCommentUpdateParser.parse_args()
    noteCommentList = db.child(childName).child('noteCommentList').get().val()
    if noteCommentList == None:
      noteCommentList = {}
    if commentID in noteCommentList:
      noteCommentList[commentID]['comment'] = args['comment']
      db.child(childName).child('noteCommentList').set(noteCommentList)
      commentDetails= noteCommentList[commentID]
    else:
      abort(400, message='comment not found')
    return commentDetails

  def delete(self, commentID):
    commentID = commentID.upper()
    noteCommentList = db.child(childName).child('noteCommentList').get().val()
    if noteCommentList == None:
      noteCommentList = {}
    if commentID in noteCommentList:
        del noteCommentList[commentID]
        db.child(childName).child('noteCommentList').set(noteCommentList)
    else:
      abort(400, message='comment not found')
    return noteCommentList

class NoteRating(Resource):
  def post(self, noteID):
    args = noteRatingParser.parse_args()
    studentID = args['studentID']
    rating = args['rating']
    if rating < 0 or rating > 5:
      abort(400, message='rating should be between 0 and 5')
    noteList = db.child(childName).child('noteList').get().val()
    if noteList == None:
      noteList = {}
    if not noteID in noteList:
      abort(400, message='note not found')
    studentList = db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    if not studentID in studentList:
      abort(400, message='student not found')
    ratingList = db.child(childName).child('ratingList').get().val()
    if ratingList == None:
      ratingList = {}
    flag = 0
    for i in ratingList:
      if ratingList[i]['noteID'] == noteID and ratingList[i]['studentID'] == studentID:
          flag = 1
          noteList[noteID]['totalRating'] = noteList[noteID]['totalRating'] - ratingList[i]['rating'] + rating
          ratingList[i]['rating'] = rating
          ratingID = i
          break
    if flag == 0:
      ratingCnt = db.child(childName).child('ratingCnt').get().val()
      if ratingCnt == None:
        ratingCnt = 0
      ratingCnt += 1
      db.child(childName).child('ratingCnt').set(ratingCnt)
      ratingID = 'RAT' + str(100 + ratingCnt)
      ratingList[ratingID] = {
        'noteID'    : noteID,
        'studentID' : studentID,
        'rating'    : rating
      }
      if 'totalRating' not in noteList[noteID]:
        noteList[noteID]['totalRating'] = 0
      if 'totalRatedStudents' not in noteList[noteID]:
        noteList[noteID]['totalRatedStudents'] = 0
      noteList[noteID]['totalRating'] = noteList[noteID]['totalRating'] + rating
      noteList[noteID]['totalRatedStudents'] = noteList[noteID]['totalRatedStudents'] + 1
    db.child(childName).child('ratingList').set(ratingList)
    db.child(childName).child('noteList').set(noteList)
    return ratingList[ratingID]

def notefilterlist(temp_note_list):
  subjectlist=[]
  for i in temp_note_list:
    subjectlist.append(temp_note_list[i]['subjectName'].lower())
    subjectlist=set(subjectlist)
    subjectlist=list(subjectlist)
  return subjectlist

def notefilter(filterlist,temp_note_list_1,cat,item):
  if cat=='subject':
    if item in filterlist:
      temp_note_list_2={}
      for j in temp_note_list_1:
        if not 'totalRatedStudents' in temp_note_list_1[j]:
          temp_note_list_1[j]['totalRatedStudents'] = 0
        if not 'totalRating' in temp_note_list_1[j]:
          temp_note_list_1[j]['totalRating'] = 0
        if temp_note_list_1[j]['totalRatedStudents'] > 0:
          temp_note_list_1[j]['averageRating'] = round(temp_note_list_1[j]['totalRating']/temp_note_list_1[j]['totalRatedStudents'])
        else:
          temp_note_list_1[j]['averageRating'] = 0
        if temp_note_list_1[j]['subjectName'].lower()==item.lower():
          temp_note_list_2[j]=temp_note_list_1[j]
      temp_note_list_1 = temp_note_list_2
  elif cat =='rating':
    temp_note_list_2={}
    for j in temp_note_list_1: 
      if not 'totalRatedStudents' in temp_note_list_1[j]:
        temp_note_list_1[j]['totalRatedStudents'] = 0
      if not 'totalRating' in temp_note_list_1[j]:
        temp_note_list_1[j]['totalRating'] = 0
      if temp_note_list_1[j]['totalRatedStudents'] > 0:
        temp_note_list_1[j]['averageRating'] = round(temp_note_list_1[j]['totalRating']/temp_note_list_1[j]['totalRatedStudents'])
      else:
        temp_note_list_1[j]['averageRating'] = 0
      if temp_note_list_1[j]['averageRating']==int(item):
        temp_note_list_2[j]=temp_note_list_1[j]
    temp_note_list_1 = temp_note_list_2
  else:
    abort(400,message='invalid category')
  return temp_note_list_1

class Filterlist(Resource):
  def post(self):
    args=filterItemListparser.parse_args()
    studentList=db.child(childName).child('studentList').get().val()
    if studentList==None:
      studentList={}
    noteList=db.child(childName).child('noteList').get().val()
    if noteList==None:
      noteList={}
    temp_note_list={}
    if args['studentID'] in studentList:
      for i in noteList:
        if args['studentID'] != noteList[i]['studentID'] and noteList[i]['status']=='approved' and noteList[i]['courseID']==studentList[args['studentID']]['courseID'] :
          temp_note_list[i]= noteList[i]
    else:
      abort(400,message='student not found') 
    filterlist=notefilterlist(temp_note_list)
    return filterlist

class Filter(Resource):
  def post(self):
    args=filterParser.parse_args()
    studentList=db.child(childName).child('studentList').get().val()
    if studentList == None:
      studentList = {}
    noteList=db.child(childName).child('noteList').get().val()
    if noteList==None:
      noteList={}
    courseList=db.child(childName).child('courseList').get().val()
    if courseList==None:
      courseList={'COURSEOTH' : {'name' : 'others'}}
      db.child(childName).child('courseList').set(courseList)
    temp_note_list_1={}
    if args['studentID'] in studentList:
      for i in noteList:
        if noteList[i]['status']=='approved' and noteList[i]['studentID']!= args['studentID'] and noteList[i]['courseID']==studentList[args['studentID']]['courseID']:
          temp_note_list_1[i]=noteList[i]
    else:
      abort(400,message='student not found')
    filterlist=notefilterlist(temp_note_list_1)
    temp_note_list_1=notefilter(filterlist,temp_note_list_1,args['cat'], args['item'])
    for i in temp_note_list_1:
      temp_note_list_1[i]['studentDetails'] = studentList[temp_note_list_1[i]['studentID']]
      temp_note_list_1[i]['courseDetails'] = courseList[temp_note_list_1[i]['courseID']]
    return temp_note_list_1

api.add_resource(StudentReg, '/student')
api.add_resource(StudentUpdate, '/student/<studentID>')
api.add_resource(StudentList, '/studentList/<courseID>')
api.add_resource(Login, '/login')
api.add_resource(CourseReg,'/course')
api.add_resource(CourseUpdate,'/course/<courseID>')
api.add_resource(NoteReg,'/note')
api.add_resource(NoteUpdate,'/note/<noteID>')
api.add_resource(NoteDocUpdate, '/noteDoc/<noteID>')
api.add_resource(StudentNotes, '/studentNotes/<studentID>')
api.add_resource(DownloadFile, '/download/<fname>')
api.add_resource(NoteAction, '/noteAction')
api.add_resource(CommunityPost, '/post/<studentID>')
api.add_resource(CommunityPostUpdate, '/postUpdate/<postID>')
api.add_resource(PostComment, '/postComment/<postID>')
api.add_resource(PostCommentUpdate, '/postCommentUpdate/<commentID>')
api.add_resource(NoteComment, '/noteComment/<noteID>')
api.add_resource(NoteCommentUpdate, '/noteCommentUpdate/<commentID>')
api.add_resource(NoteRating, '/noteRating/<noteID>')
api.add_resource(Filterlist,'/filterlist')
api.add_resource(Filter,'/filter')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8000)