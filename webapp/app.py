from flask import Flask,render_template, request, make_response, redirect, url_for,session
import requests

app=Flask(__name__)
app.secret_key='abcd'

base_url='studentcommunity.web.app'
base_url='http://127.0.0.1:8000'

@app.route('/')
def studentHome():
	if 'student' in session:
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		response = requests.get(base_url+'/studentNotes/' + studentID)
		studentNotesDict = response.json()
		noteList = studentNotesDict['others']
		response=requests.post(base_url+'/filterlist',data={'studentID':studentID})
		subjectList=response.json()
		return render_template('student_home.html',studentDetails=studentDetails, noteList=noteList, subjectList=subjectList)
	else:
		response = requests.get(base_url+'/studentNotes/nil')
		studentNotesDict = response.json()
		noteList = studentNotesDict['all']
		return render_template('guest_home.html', noteList=noteList)

@app.route('/home/<cat>/<item>')
def filterStudentHome(cat,item):
	if 'student' in session:
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		response=requests.post(base_url+'/filter',data={'studentID': studentID, 'cat' : cat, 'item' : item})
		noteList = response.json()
		response=requests.post(base_url+'/filterlist',data={'studentID':studentID})
		subjectList=response.json()
		return render_template('student_home.html',studentDetails=studentDetails, noteList=noteList, subjectList=subjectList)
	else:
		response = requests.get(base_url+'/studentNotes/nil')
		studentNotesDict = response.json()
		noteList = studentNotesDict['all']
		return render_template('guest_home.html', noteList=noteList)

@app.route('/filter',methods=['POST','GET'])
def filter():
	if 'student' in session:
		if request.method=='POST':
			userInput=request.form.to_dict()
			return redirect(url_for('filterStudentHome', cat=userInput['cat'], item=userInput['item']))
	else:
		return redirect(url_for('studentHome'))

@app.route('/admin')
def adminHome():
	warning=request.cookies.get('warning')
	if warning == None:
		warning = ''
	if 'admin' in session:
		response = requests.get(base_url+'/course')
		courseList = response.json()
		return render_template('admin_home.html', courseList=courseList, warning=warning)
	else:
		return render_template('login.html', session='admin', warning=warning)

@app.route('/studentReg', methods=['POST','GET'])
def studentReg():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		userImg = request.files['photo']
		files = {'photo' : (userImg.filename, userImg, userImg.content_type)}	
		response = requests.post(base_url + '/student', data=userInput, files=files)
		if response.status_code == 400:
			resp=make_response(redirect(url_for('studentLogin')))
			resp.set_cookie('warning',response.json()['message'], max_age=5)
			return resp
		elif response.status_code == 200:
			resp=make_response(redirect(url_for('studentLogin')))
			resp.set_cookie('warning','student registered successfully', max_age=5)
			return resp

@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		response = requests.post(base_url+'/login', data=userInput)
		loginID = response.json()
		if userInput['cat'] == 'student':
			if loginID != '':
				session['student'] = loginID
				return redirect(url_for('studentHome'))
			else:
				resp=make_response(redirect(url_for('studentLogin')))
				resp.set_cookie('warning','wrong email or password', max_age=5)
				return resp
		elif userInput['cat'] == 'admin':
			if loginID == 'admin':
				session['admin'] = loginID
				return redirect(url_for('adminHome'))
			else:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning','wrong email or password', max_age=5)
				return resp

@app.route('/studentLogin')
def studentLogin():
	response = requests.get(base_url+'/course')
	courseList = response.json()
	warning=request.cookies.get('warning')
	if warning == None:
		warning = ''
	return render_template('login.html', courseList=courseList, session='student', warning=warning)

@app.route('/studentProfile')
def studentProfile():
	if 'student' in session:
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		return render_template('student_profile.html', studentDetails=studentDetails)
	else:
		return redirect(url_for('studentHome'))

@app.route('/editStudentProfile')
def editStudentProfile():
	if 'student' in session:
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		response = requests.get(base_url+'/course')
		courseList = response.json()
		return render_template('edit_student_profile.html', studentDetails=studentDetails, courseList=courseList)
	else:
		return redirect(url_for('studentHome'))

@app.route('/studentProfileUpdate', methods=['POST','GET'])
def studentProfileUpdate():
	if 'student' in session:
		if request.method == 'POST':
			studentID = session['student']
			userInput = request.form.to_dict()
			userImg = request.files['photo']
			if userImg:
				files = {'photo' : (userImg.filename, userImg, userImg.content_type)}
				requests.put(base_url + '/student/' + studentID, data=userInput, files=files)
			else:	
				requests.put(base_url + '/student/' + studentID, data=userInput)
			return redirect(url_for('studentProfile'))
	else:
		return redirect(url_for('studentHome'))

@app.route('/studentLogout')
def studentLogout():
	if 'student' in session:
		session.pop('student',None)
	return redirect(url_for('studentHome'))

@app.route('/adminLogout')
def adminLogout():
	if 'admin' in session:
		session.pop('admin',None)
	return redirect(url_for('adminHome'))

@app.route('/courseReg', methods=['POST','GET'])
def courseReg():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url + '/course', data=userInput)
			if response.status_code == 400:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning',response.json()['message'], max_age=5)
				return resp
			elif response.status_code == 200:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning','course registered successfully', max_age=5)
				return resp
	return redirect(url_for('adminHome'))

@app.route('/courseUpdate', methods=['POST','GET'])
def courseUpdate():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.put(base_url + '/course/' + userInput['courseID'], data=userInput)
			if response.status_code == 400:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning',response.json()['message'], max_age=5)
				return resp
			elif response.status_code == 200:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning','course updated successfully', max_age=5)
				return resp
	return redirect(url_for('adminHome'))

@app.route('/courseDelete', methods=['POST','GET'])
def courseDelete():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.delete(base_url + '/course/' + userInput['courseID'])
			if response.status_code == 200:
				resp=make_response(redirect(url_for('adminHome')))
				resp.set_cookie('warning','course deleted successfully', max_age=5)
				return resp
	return redirect(url_for('adminHome'))

@app.route('/notes')
def uploadNotesPage():
	if 'student' in session:
		warning=request.cookies.get('warning')
		if warning == None:
			warning = ''
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		return render_template('student_upload_notes.html', studentDetails=studentDetails, warning=warning)
	else:
		return redirect(url_for('studentHome'))

@app.route('/noteUpload', methods=['POST','GET'])
def noteUpload():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['studentID'] = session['student']
			userDoc = request.files.getlist('doc')
			mulFiles = []
			for i in userDoc:
				mulFiles.append(('doc', (i.filename, i, i.content_type)))
			response = requests.post(base_url + '/note', data=userInput, files=mulFiles)
			if response.status_code == 200:
				resp=make_response( redirect(url_for('uploadNotesPage')))
				resp.set_cookie('warning','note uploaded successfully', max_age=5)
				return resp
	else:
		return redirect(url_for('studentHome'))

@app.route('/studentNotes')
def studentNotes():
	if 'student' in session:
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		response = requests.get(base_url+'/studentNotes/' + studentID)
		studentNotesDict = response.json()
		notApprovedNoteList = studentNotesDict['notApproved']
		approvedNoteList = studentNotesDict['approved']
		blockedNoteList = studentNotesDict['blocked']
		return render_template('student_notes.html', studentDetails=studentDetails, notApprovedNoteList=notApprovedNoteList, approvedNoteList=approvedNoteList, blockedNoteList=blockedNoteList)
	else:
		return redirect(url_for('studentHome'))

@app.route('/adminNoteList')
def adminNoteList():
	if 'admin' in session:
		response = requests.get(base_url+'/note')
		noteDict = response.json()
		notApprovedNoteList = noteDict['notApproved']
		approvedNoteList = noteDict['approved']
		blockedNoteList = noteDict['blocked']
		return render_template('admin_notes.html', notApprovedNoteList=notApprovedNoteList, approvedNoteList=approvedNoteList, blockedNoteList=blockedNoteList)
	else:
		return redirect(url_for('adminHome'))

@app.route('/adminNoteProfile/<noteID>')
def adminNoteProfile(noteID):
	if 'admin' in session:
		response = requests.get(base_url+'/note/' + noteID)
		noteDetails = response.json()
		response = requests.get(base_url + '/noteComment/' + noteID)
		noteComment = response.json()
		warning = request.cookies.get('warning')
		if warning == None:
			warning = ''
		return render_template('admin_note_profile.html', noteID=noteID, noteComment=noteComment, noteDetails=noteDetails, base_url=base_url, warning=warning)
	else:
		return redirect(url_for('adminHome'))

@app.route('/othNoteProfile/<noteID>')
def othNoteProfile(noteID):
	if 'student' in session:
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		response = requests.get(base_url+'/note/' + noteID)
		noteDetails = response.json()
		response = requests.get(base_url + '/noteComment/' + noteID)
		noteComment = response.json()
		return render_template('student_oth_note_profile.html', studentID=studentID, noteID=noteID, noteDetails=noteDetails, noteComment=noteComment, base_url=base_url, studentDetails=studentDetails)
	else:
		return redirect(url_for('studentHome'))

@app.route('/studentNoteProfile/<noteID>')
def studentNoteProfile(noteID):
	if 'student' in session:
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		response = requests.get(base_url+'/note/' + noteID)
		noteDetails = response.json()
		response = requests.get(base_url + '/noteComment/' + noteID)
		noteComment = response.json()
		return render_template('student_note_profile.html', studentID=studentID, noteID=noteID, noteDetails=noteDetails, noteComment=noteComment, base_url=base_url, studentDetails=studentDetails)
	else:
		return redirect(url_for('studentHome'))

@app.route('/noteAction', methods=['POST','GET'])
def noteAction():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url+'/noteAction', data=userInput)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('adminNoteProfile', noteID=userInput['noteID'])))
				resp.set_cookie('warning', userInput['action'] + ' successfully', max_age=5)
				return resp
	else:
		return redirect(url_for('adminHome'))

@app.route('/community')
def communityHomePage():
	if 'student' in session:
		warning=request.cookies.get('warning')
		if warning == None:
			warning = ''
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		response = requests.get(base_url + '/post/' + studentID)
		postDict = response.json()
		myPost = postDict['myPost']
		otherPost = postDict['otherPost']
		return render_template('community_home.html', studentDetails=studentDetails, myPost=myPost, otherPost=otherPost, warning=warning)
	else:
		return redirect(url_for('studentHome'))

@app.route('/addPost', methods=['POST','GET'])
def addPost():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			studentID = session['student']
			postImg = request.files['photo']
			if postImg:
				files = {'photo' : (postImg.filename, postImg, postImg.content_type)}
				response = requests.post(base_url + '/post/' + studentID, data=userInput, files=files)
			else:	
				response = requests.post(base_url + '/post/' + studentID, data=userInput)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('communityHomePage')))
				resp.set_cookie('warning','post added successfully', max_age=5)
				return resp
	else:
		return redirect(url_for('studentHome'))

@app.route('/updatePost', methods=['POST','GET'])
def updatePost():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			postImg = request.files['photo']
			if postImg:
				files = {'photo' : (postImg.filename, postImg, postImg.content_type)}
				requests.put(base_url + '/postUpdate/' + userInput['postID'], files=files)
			response = requests.put(base_url + '/postUpdate/' + userInput['postID'], data=userInput)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('communityHomePage')))
				resp.set_cookie('warning','post updated successfully', max_age=5)
				return resp
	else:
		return redirect(url_for('studentHome'))

@app.route('/deletePost', methods=['POST','GET'])
def deletePost():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.delete(base_url + '/postUpdate/' + userInput['postID'])
			if response.status_code == 200:
				resp=make_response(redirect(url_for('communityHomePage')))
				resp.set_cookie('warning','post deleted successfully', max_age=5)
				return resp
	else:
		return redirect(url_for('studentHome'))

@app.route('/postComments/<postID>')
def postComments(postID):
	if 'student' in session:
		studentID = session['student']
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		response = requests.get(base_url + '/postUpdate/' + postID)
		postDetails = response.json()
		response = requests.get(base_url + '/postComment/' + postID)
		postComment = response.json()
		return render_template('post_details.html', studentID=studentID, studentDetails=studentDetails, postID=postID, postDetails=postDetails, postComment=postComment)
	else:
		return redirect(url_for('studentHome'))

@app.route('/addPostComment', methods=['POST', 'GET'])
def addPostComment():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['studentID'] = session['student']
			requests.post(base_url + '/postComment/' + userInput['postID'], data=userInput)
			return redirect(url_for('postComments', postID=userInput['postID']))
	else:
		return redirect(url_for('studentHome'))

@app.route('/editPostComment', methods=['POST', 'GET'])
def editPostComment():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.put(base_url + '/postCommentUpdate/' + userInput['commentID'], data=userInput)
			return redirect(url_for('postComments', postID=userInput['postID']))
	else:
		return redirect(url_for('studentHome'))

@app.route('/deletePostComment', methods=['POST', 'GET'])
def deletePostComment():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.delete(base_url + '/postCommentUpdate/' + userInput['commentID'], data=userInput)
			return redirect(url_for('postComments', postID=userInput['postID']))
	else:
		return redirect(url_for('studentHome'))

@app.route('/addNoteCommentOth', methods=['POST', 'GET'])
def addNoteCommentOth():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['studentID'] = session['student']
			requests.post(base_url + '/noteComment/' + userInput['noteID'], data=userInput)
			return redirect(url_for('othNoteProfile', noteID=userInput['noteID']))
	else:
		return redirect(url_for('studentHome'))

@app.route('/editNoteCommentOth', methods=['POST', 'GET'])
def editNoteCommentOth():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.put(base_url + '/noteCommentUpdate/' + userInput['commentID'], data=userInput)
			return redirect(url_for('othNoteProfile', noteID=userInput['noteID']))
	else:
		return redirect(url_for('studentHome'))

@app.route('/deleteNoteCommentOth', methods=['POST', 'GET'])
def deleteNoteCommentOth():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.delete(base_url + '/noteCommentUpdate/' + userInput['commentID'], data=userInput)
			return redirect(url_for('othNoteProfile', noteID=userInput['noteID']))
	else:
		return redirect(url_for('studentHome')) 

@app.route('/addNoteCommentOwn', methods=['POST', 'GET'])
def addNoteCommentOwn():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['studentID'] = session['student']
			requests.post(base_url + '/noteComment/' + userInput['noteID'], data=userInput)
			return redirect(url_for('studentNoteProfile', noteID=userInput['noteID']))
	else:
		return redirect(url_for('studentHome'))

@app.route('/editNoteCommentOwn', methods=['POST', 'GET'])
def editNoteCommentOwn():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.put(base_url + '/noteCommentUpdate/' + userInput['commentID'], data=userInput)
			return redirect(url_for('studentNoteProfile', noteID=userInput['noteID']))
	else:
		return redirect(url_for('studentHome'))

@app.route('/deleteNoteCommentOwn', methods=['POST', 'GET'])
def deleteNoteCommentOwn():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.delete(base_url + '/noteCommentUpdate/' + userInput['commentID'], data=userInput)
			return redirect(url_for('studentNoteProfile', noteID=userInput['noteID']))
	else:
		return redirect(url_for('studentHome'))

@app.route('/deleteNoteCommentAdmin', methods=['POST', 'GET'])
def deleteNoteCommentAdmin():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.delete(base_url + '/noteCommentUpdate/' + userInput['commentID'], data=userInput)
			if response.status_code == 200:
				resp=make_response(redirect(url_for('adminNoteProfile', noteID=userInput['noteID'])))
				resp.set_cookie('warning', 'comment delete successfully', max_age=5)
				return resp
	else:
		return redirect(url_for('adminHome'))

@app.route('/adminStudentList/<courseID>')
def adminStudentList(courseID):
	if 'admin' in session:
		response = requests.get(base_url+'/studentList/' + courseID)
		studentList = response.json()
		response = requests.get(base_url+'/course')
		courseList = response.json()
		courseDetails = courseList[courseID]
		return render_template('admin_student_list.html', courseDetails=courseDetails, studentList=studentList)
	else:
		return redirect(url_for('adminHome'))

@app.route('/adminStudentDetails/<studentID>')
def adminStudentDetails(studentID):
	if 'admin' in session:
		response = requests.get(base_url+'/student/' + studentID)
		studentDetails = response.json()
		response = requests.get(base_url+'/studentNotes/' + studentID)
		studentNotesDict = response.json()
		notApprovedNoteList = studentNotesDict['notApproved']
		approvedNoteList = studentNotesDict['approved']
		blockedNoteList = studentNotesDict['blocked']
		return render_template('admin_student_details.html', studentDetails=studentDetails, notApprovedNoteList=notApprovedNoteList, approvedNoteList=approvedNoteList, blockedNoteList=blockedNoteList)
	else:
		return redirect(url_for('adminHome'))

@app.route('/rateNote', methods=['POST', 'GET'])
def rateNote():
	if 'student' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			studentID = session['student']
			requests.post(base_url + '/noteRating/' + userInput['noteID'], data={'studentID' : studentID, 'rating' : userInput['rating']})
			return redirect(url_for('othNoteProfile', noteID=userInput['noteID']))
	else:
		return redirect(url_for('studentHome'))

if __name__=='__main__':
	app.run(debug=True, host='0.0.0.0')