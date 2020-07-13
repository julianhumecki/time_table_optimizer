import numpy as np 

from flask import Flask, render_template, request, session, redirect
from flask_session import Session


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

colorScheme = ['#08348C','#07418C','#BDD3D8','#F27830','#F24405','#2B7B89']
dayToNumber = {
	"monday":0,
	"tuesday":1,
	"wednesday":2,
	"thursday":3,
	"friday":4
}



@app.route("/", methods=["GET","POST"])
def index():
	courseNum = 0
	if request.method == "POST":
		value = int(request.form.get("number"))
		courseNum = value
		session["numberOfCourses"] = value
	

	return render_template("add_courses.html", courseNumber=courseNum)

@app.route("/instructions", methods=["GET"])
def instructions():
	return "instructions"

@app.route("/schedule/<int:schedule_id>", methods=["GET"])
def schedule_index(schedule_id):
	clear = error_check(schedule_id)
	#error occurs
	if clear[0]:
		return render_template("schedule.html", error_message=clear[1],error=clear[0])

	#no error
	#print(session["hourMap"][schedule_id-1])
	#input(":")	
	# print(session["hourMap"][schedule_id-1][97][0].split()[0].lower())
	# input(":")
	return render_template("schedule.html", topFive=session["hourMap"][schedule_id-1], topN=len(session["hourMap"]), colorMap=session['colorMap'],error_message=clear[1], error=clear[0], id=schedule_id)

@app.route("/inputError",methods=["GET"])
def error_input():
	#will return a session["input_error"]
	return session["input_error"]

@app.route("/schedule",methods=["POST"])
def schedule():
	#must filter out duplicate times
	coursesToTimeslots = dict()
	colorMap = dict()
	indexer = 0
	for i in range(0, session["numberOfCourses"]):
		info_about_course = dict()
		name = request.form.get("course-"+str(i)+"-code")
		
		lect_times = request.form.get("lect-"+str(i)).strip().split(";")
		lecturing = list()
		for time in lect_times:
			#remove whitespaces and split
			cleaned_up = time.strip().split(",").copy()
			#check input for proper form
			lecturing.append(cleaned_up)

		tut_times = request.form.get("tut-"+str(i)).strip().split(';')
		pra_times = request.form.get("pra-"+str(i)).strip().split(';')
		#lec
		info_about_course['Lec'] = lecturing.copy()
		
		#check tutorial for dne entry
		if len(tut_times) == 1 and tut_times[0].lower() == "dne":
			info_about_course['Tut'] = None
		#if not dne parse appropriately
		else:
			#info_about_course['Tut'] = tut_times.copy()
			temp_tut = list()
			for time in tut_times:
				cleaned_up = time.strip().split(",").copy()
				temp_tut.append(cleaned_up)
			info_about_course["Tut"] = temp_tut.copy()

		#check tutorial for dne entry
		if len(pra_times) == 1 and pra_times[0].lower() == "dne":
			info_about_course['Pra'] = None
		#if not parse it for times
		else:
			temp_pra = list()
			for time in pra_times:
				cleaned_up = time.strip().split(",").copy()
				temp_pra.append(cleaned_up)
			info_about_course["Pra"] = temp_pra.copy()

		

		colorMap[name.lower()] =  colorScheme[indexer]

		coursesToTimeslots[name.lower()] = info_about_course.copy()
		indexer += 1

	#print(coursesToTimeslots)

	#Tuesday 10 to 11, Wednesday 10 to 11, Friday 10 to 11
	#Tuesday 13 to 14
	#Wednesday 15 to 16
	# courseOne = dict()
	# courseOne["Lec"] = [["Tuesday 10 to 11", "Wednesday 10 to 11", "Friday 10 to 11"]] 
	# courseOne["Tut"] = ["Thursday 9 to 11", "Friday 16 to 18", "Friday 13 to 15"]
	# courseOne["Pra"] = None
	# coursesToTimeslots["ECE302"] = courseOne

	# courseTwo = dict()
	# courseTwo["Lec"] = [["Monday 13 to 14", "Tuesday 14 to 15", "Thursday 13 to 14"]] 
	# courseTwo["Tut"] = ["Thursday 18 to 19"]
	# courseTwo["Pra"] = ["Monday 15 to 18","Thursday 15 to 18","Wednesday 12 to 15","Friday 9 to 12"]
	# coursesToTimeslots["ECE320"] = courseTwo

	# courseThree = dict()
	# courseThree["Lec"] = [["Monday 11 to 12", "Wednesday 11 to 12", "Friday 11 to 12"]] 
	# courseThree["Tut"] = ["Monday 9 to 11","Thursday 9 to 11","Wednesday 16 to 18"]
	# courseThree["Pra"] = None
	# coursesToTimeslots["ECE345"] = courseThree


	# courseFour = dict()
	# courseFour["Lec"] = [["Tuesday 13 to 14", "Thursday 13 to 14", "Friday 14 to 15"]] 
	# courseFour["Tut"] = ["Thursday 14 to 15", "Monday 18 to 19"]
	# courseFour["Pra"] = ["Wednesday 15 to 18","Monday 9 to 12"]
	# coursesToTimeslots["ECE361"] = courseFour

	# courseFive = dict()
	# courseFive["Lec"] = [["Monday 10 to 12", "Wednesday 11 to 12"], ["Monday 14 to 16","Wednesday 14 to 15"]] 
	# courseFive["Tut"] = None
	# courseFive["Pra"] = None
	# coursesToTimeslots["CSC343"] = courseFive

	# courseSix = dict()
	# courseSix["Lec"] = [["Tuesday 12 to 15"], ["Tuesday 15 to 18"]] 
	# courseSix["Tut"] = None
	# courseSix["Pra"] = None
	# coursesToTimeslots["APS444"] = courseSix

	# #returns a dictionary containing info about each course 
	# #times are now lists in integer form
	# # 25,26,27 represents a class on Tuesday from 1am to 3am
	newTimes = convertTimesToCommonTime(coursesToTimeslots)
	if type(newTimes) == str:
		session["input_error"] = newTimes
		return redirect("/inputError")
	#print(coursesToTimeslots)
	
	#print(newTimes)
#______________________________________________________________________________________________________________
	courseName, courseInfo = getNameAndInfo(newTimes)
	#print(courseName)
	#print(courseInfo)
	all_time_combos_of_courses = getAllPossibleValues(courseName, courseInfo)
	#print(all_time_combos_of_courses)
	topFive = list()
	topFiveType = list()
	#next step: find optimized schedule
	optimize_schedule(courseName, all_time_combos_of_courses, 0, dict(),dict(),topFive,topFiveType, newTimes)
	# #print(len(topFive))
	#special_print(topFive, topFiveType)
	#print(topFiveType)
	# #if you want to insert a time into the table you need it worked out before hand
	# #i.e dictionary with keys that are hours, values: list of strings (course code, lec, prac,)
	# #print(newTimes)
	
	hourMap = putIntoCalendarForm(topFive,topFiveType ,newTimes)
	#print(f"Hour Maps: {hourMap}")
	# #print(hourMap)
	session["colorMap"] = colorMap
	session["hourMap"] = hourMap
#_______________________________________________________________________________________________________________
	#print(overlaps(hourMap[0], newTimes))
	#rewrite overlaps fcn it is wrong!
	#input(":")
	return redirect("/schedule/1")
	#return redirect("/")

def putIntoCalendarForm(topFive, topFiveType, newTimes):
	#print(f"Top five: {topFive}")
	# print(f"New times: {newTimes}")
	#print(f"Types: {topFiveType}")
	#input(";")

	indexer = 0
	times = list()
	for number, mapping in topFive:
		#list of tuples
		hourMap = dict()
		for key in mapping:
			inner_indexer = 0
			for index, time in enumerate(mapping[key]):
				start = time[0]
				end = time[1]

				#not inclusive of end
				for count in range(start, end):
					to_add = key.upper() + " " + topFiveType[indexer][key][inner_indexer]
					if not count in hourMap:
						hourMap[count] = [to_add]
					else:
						hourMap[count].append(to_add)

				inner_indexer += 1

		indexer += 1
		times.append(hourMap.copy())
	return times

#keep track of times
def optimize_schedule(courseNames, all_time_combos_of_courses, courseCount, overlapTracker,overlapTrackerType,topFiveSchedules,topFiveType,newTimes):

	#finished this round
	if courseCount == len(courseNames):
		#cool
		#evaluate the solution
		#for now our metric will be the number of overlaps
		#we'll see how that goes
		value = overlaps(overlapTracker,newTimes)
		#input(":")
		#print(f"VALUES----------------------------:{overlapTracker}")
		#print(f"TYPE------------------------------:{overlapTrackerType}")
		insertValueIntoTopFive(value, overlapTracker,overlapTrackerType,topFiveSchedules,topFiveType)
		
		return

	else:
		courseName = courseNames[courseCount]
		for combo in all_time_combos_of_courses[courseName]:
			#print(combo)
			times = list()
			types = list()
			#get lect times
			for time in combo[0]:
				times.append((time[0],time[-1]))
				types.append("LEC")

			#get tut times
			if combo[1]:
				for time in combo[1]:
					times.append((time[0],time[-1]))
					types.append("TUT")

			#get pra times
			if combo[2]:
				for time in combo[2]:
					times.append((time[0],time[-1]))
					types.append("PRA")
				#times.append((combo[2][0],combo[2][-1]))

			overlapTracker[courseName] = times
			overlapTrackerType[courseName] = types
			optimize_schedule(courseNames, all_time_combos_of_courses, (courseCount+1), overlapTracker, overlapTrackerType, topFiveSchedules, topFiveType,newTimes)

		return

def special_print(topFive, topFiveType):
	for one,two in zip(topFive, topFiveType):
		print(one[0])
		print(one[1])
		print(f"TYPE:{two}")
		print()

	#double checking uniqueness	
	# for one in topFive:
	# 	for two in topFive:
	# 		print(one[1] == two[1])
	# 	print()
	return


def insertValueIntoTopFive(value, overlapTracker,overlapTrackerType,topFiveSchedules,topFiveType):
	to_insert = (value,overlapTracker.copy())
	typed = overlapTrackerType.copy()
	if len(topFiveSchedules) == 0:
		topFiveSchedules.append(to_insert)
		topFiveType.append(typed)
		return
	else:
		count = 0
		taskCopy = topFiveSchedules.copy()
		for task in taskCopy:
			if(value < task[0]):
				topFiveSchedules.insert(count, to_insert)
				topFiveType.insert(count, typed)

				if len(topFiveSchedules) > 5:
					topFiveSchedules.pop()
					topFiveType.pop()

				return
			count +=1
		if len(taskCopy) < 5:
			topFiveSchedules.append(to_insert)
			topFiveType.append(typed)
		return 

#all_overlaps is a dictionary
def overlaps(all_overlaps, newTimes):
	
	numberOfConflicts = 0
	hourMap = dict()
	for key in all_overlaps:
		#list of tuples
		for time in all_overlaps[key]:
			start = time[0]
			end = time[1]

			#not inclusive of end
			for count in range(start, end):
				
				if not count in hourMap:
					hourMap[count] = [key]
				else:
					hourMap[count].append(key)

	for key in hourMap:
		if len(hourMap[key]) > 1:
			numberOfConflicts += 1

	return numberOfConflicts



def getAllPossibleValues(courseNames, coursesInfo):
	all_combos = dict()
	#options are
	#arrays of length 3
	#[lec time(s), tut time, pra time ]
	for course_name, course_info in zip(courseNames, coursesInfo):
		all_combos[course_name] = []
		instance = list()
		#print(course_name)
		for lect_times in course_info["Lec"]:
			instance.append(lect_times)
			#if tut is not None
			if course_info["Tut"]:
				for tut_time in course_info["Tut"]:
					#print(f"Tut time: {tut_time}")
					instance.append(tut_time)
					if course_info["Pra"]:
						for pra_time in course_info["Pra"]:
							instance.append(pra_time)
							#print(f"added: {instance}")
							all_combos[course_name].append(instance.copy())
							instance.pop()
					#if there is a tut but no practical
					else:
						instance.append(None)
						#print(f"added: {instance}")
						all_combos[course_name].append(instance.copy())
						instance.remove(None)

					instance.pop()

			#covers case of there being only a pract
			elif course_info["Pra"]:
				#adding a null tut time
				instance.append(None)
				for pra_time in course_info["Pra"]:
					instance.append(pra_time)
					#print(f"added: {instance}")
					all_combos[course_name].append(instance.copy())
					instance.pop()
				instance.remove(None)
			else:
				instance.append(None)
				instance.append(None)		
				#print(f"added: {instance}")
				all_combos[course_name].append(instance.copy())
				instance.remove(None)
				instance.remove(None)
			#remove lect time
			instance.pop()

	return all_combos


def getNameAndInfo(newTimes):
	courseName = list()
	courseInfo = list()
	for course in newTimes:
		courseName.append(course)
		courseInfo.append(newTimes[course])
	return courseName, courseInfo

def convertTimesToCommonTime(coursesToTimeslots):
	newTimes = dict()
	HOURS_IN_DAY = 24
	for course in coursesToTimeslots:
		
		#print()
		#print(course)
		courseSplit = dict()

		#print("Lectures:")
		timing = list()
		for timeslots in coursesToTimeslots[course]["Lec"]:
			sub_timing = list()
			for time in timeslots:
				times = time.split()
				if not len(times) == 4:
					return course +"'s Lecture input is not following this form: day start_time to end_time"
				#print(times)
				try:
					attendStart = dayToNumber[times[0].lower().strip()]*24 + int(times[1].strip())
					attendEnd = dayToNumber[times[0].lower().strip()]*24 + int(times[3].strip())
					sub_timing.append(list(np.arange(attendStart, attendEnd+1)))
				except:
					return course +"'s Lecture Input: You can only enter a day from Monday to Friday inclusive, we need weekends off! Also, make sure your start time and end time are some integers from 9 to 21 inclusive"

			timing.append(sub_timing)

		courseSplit['Lec'] = timing

		#print("Tutorials:")
		if not coursesToTimeslots[course]["Tut"] == None:
			timing = list()
			for timeslots in coursesToTimeslots[course]["Tut"]:
				sub_timing = list()
				for time in timeslots:
					times = time.split()
					if not len(times) == 4:
						return course +"'s Tutorial input is not following this form: day start_time to end_time or simply dne"
					#print(time)
					try:
						attendStart = dayToNumber[times[0].lower().strip()]*24 + int(times[1].strip())
						attendEnd = dayToNumber[times[0].lower().strip()]*24 + int(times[3].strip())
						sub_timing.append(list(np.arange(attendStart, attendEnd+1)))
					except:
						return course +"'s Tutorial Input: You can only enter a day from Monday to Friday inclusive, we need weekends off! Also, make sure your start time and end time are some integers from 9 to 21 inclusive"

				timing.append(sub_timing)

			courseSplit["Tut"] = timing
		else:
			courseSplit["Tut"] = None

		if not coursesToTimeslots[course]["Pra"] == None:
			timing = list()
			for timeslots in coursesToTimeslots[course]["Pra"]:
				sub_timing = list()
				for times in timeslots:
					time = times.split()
					if not len(time) == 4:
						return course +"'s Practical input is not following this form: day start_time to end_time or simply dne"
					
					try:
						attendStart = dayToNumber[time[0].lower().strip()]*24 + int(time[1].strip())
						attendEnd = dayToNumber[time[0].lower().strip()]*24 + int(time[3].strip())
						sub_timing.append(list(np.arange(attendStart, attendEnd+1)))
					except:
						return course +"'s Practical Input: You can only enter a day from Monday to Friday inclusive, we need weekends off! Also, make sure your start time and end time are some integers from 9 to 21 inclusive"

				timing.append(sub_timing)
			
			courseSplit["Pra"] = timing
		
		else:
			courseSplit["Pra"] = None

		newTimes[course] = courseSplit

	return newTimes

def error_check(schedule_id):
	if session.get("hourMap") is None or session.get("colorMap") is None:
		return [True, "Please fill out the main page before coming here please..."]
	if len(session["hourMap"]) < schedule_id or schedule_id <= 0:
		return [True,"That schedule number does not exist. You have "+str(len(session["hourMap"])) + " top schedule(s)"]
	return [False, str()]


if __name__ == "__main__":
    app.run()
