#!python3
import os
import re
from tkinter import *
from tkinter import messagebox

##########################################################################
# The stuff between this box and the next box is JUST the GUI; it is not #
# critical to the operation of the program, just meant for convenience.  #
# If this part ever breaks, you can just manually go in with a text 	 # 
# editor and put in the correct date as the only line in data.dat and all#
# that follows will still work as it should. (if this happens delete GUI)#
##########################################################################

dateFileName = './data/date.dat'

dateFile = open(dateFileName, 'a+')
dateFile.seek(0)
date = dateFile.readline()

dateFile.close()

def quit():
	top.quit()

def update():
	newDate = E1.get()
	if re.match(r'\d{4}\-\d\d-\d\d', newDate):
		dateFile = open(dateFileName, 'w+')
		dateFile.seek(0)
		dateFile.truncate()
		dateFile.write(newDate)
		dateFile.close()
		date = newDate
		top.quit()
	else:
		messagebox.showwarning('Format Error', 
			'Your input did not match the format\n'+
			'YYYY-MM-DD. Please try again.')

top = Tk()
L1 = Label(top, text = 'The current expiration date is\n' +
	date +'. If that date is\nfrom before the start of the\n' +
	'current semester, it should be\nchanged. Enter a new date below\n'+
	'and click "Update" to change it,\nor click "Keep" to proceed.\n' +
	'(Format: YYYY-MM-DD)')
L1.pack( side = TOP )

inputFrame = Frame(top)

L2 = Label( inputFrame, text='New Date:')
L2.pack( side = LEFT )
E1 = Entry( inputFrame, bd =5)
E1.pack( side = RIGHT, expand = YES, fill = X)

inputFrame.pack()

buttonFrame = Frame(top)

B1 = Button(buttonFrame, anchor = 'sw', text = 'Update', command = update)
B1.pack(side = LEFT)
B2 = Button(buttonFrame, anchor = 'se', text = 'Keep', command = quit)
B2.pack(side = RIGHT)

buttonFrame.pack( side = BOTTOM)

top.mainloop()

##########################################################################
#																		 #
#							  GUI ENDS HERE								 #
#																		 #
##########################################################################

#retrieve date that was just set by GUI
dateFile = open(dateFileName)

oclcExpirationDate = dateFile.readline()
oclcExpirationDate = oclcExpirationDate.strip() + 'T23:59:59'

dateFile.close()

#fields required by OCLC in the order they are required
outputFields = ['prefix','givenName','middleName','familyName','suffix',
				'nickname','canSelfEdit','dateOfBirth','gender','institutionId',
				'barcode','idAtSource','sourceSystem','borrowerCategory',
				'circRegistrationDate','oclcExpirationDate','homeBranch',
				'primaryStreetAddressLine1','primaryStreetAddressLine2',
				'primaryCityOrLocality','primaryStateOrProvince','primaryPostalCode',
				'primaryCountry','primaryPhone','secondaryStreetAddressLine1',
				'secondaryStreetAddressLine2','secondaryCityOrLocality',
				'secondaryStateOrProvince','secondaryPostalCode','secondaryCountry',
				'secondaryPhone','emailAddress','mobilePhone','notificationEmail',
				'notificationTextPhone','patronNotes','photoURL','customdata1',
				'customdata2','customdata3','customdata4','username','illId',
				'illApprovalStatus','illPatronType','illPickupLocation']

#these are the upper limits on how long each output field can be, in characters
outputFieldCharacterLimits = [10, 50, 100, 50, 10, 
							  50, 10, 10, 10, 100, # 5 fields per row
							  20, 50, 255, 30, 10,
							  20, 100, 120, 120, 50,
							  120, 20, 120, 50, 120,
							  120, 50, 120, 20, 120, 
							  50, 254, 50, 4096, 4096, 
							  255, 8192, 8192, 8192, 8192,
							  8192, 50, 254, 10]

# this dict is used for easy lookup of max lengths when writing to the output file
lengths = dict(zip(outputFields, outputFieldCharacterLimits))

# These are the columns from Argos. Should that system ever change, you can just
# update the list to reflect the new column schema, changing names to their oclc
# versions where they exist.

inputFields = [ #comments indicate original name of renamed fields in Argos output
			   "barcode", #ID
			   "givenName", #FIRST_NAME
			   "middleName", #MI_NAME
			   "familyName", #LAST_NAME
			   "LEVL_CODE", #N/A
			   "COLL_CODE1", #N/A
			   "deg1", #N/A
			   "deg2", #N/A
			   "m1", #N/A
			   "m2", #N/A
			   "m1_2", #N/A
			   "m2_2", #N/A
			   "credit_hours", #N/A
			   "primaryStreetAddressLine1", #CAMPUS_BOX
			   "secondaryStreetAddressLine1", #STREET1
			   "secondaryStreetAddressLine2", #STREET2
			   "secondaryCityOrLocality", #CITY
			   "secondaryStateOrProvince", #STATE
			   "secondaryPostalCode", #ZIP
			   "secondaryCountry", #COUNTRY
			   "emailAddress" #EMAIL
			   ]

# The basic idea here is we build up a dict of the data that exists in the input,
# then use this function to extract it piece by piece to make the output.
def extractField(field, patron):
	if field in patron: #check field exists in patron
		length = lengths[field] #pull max length of field from dict
		return patron[field][:length] #cut off string after the many chars
	else:
		return '' #if field does not exist, return empty string

inputDir = './input'

try:
	# Listdir will list all files in input directory. The argos report file names
	# are such that alphabetical order is chronological, so selecting the last
	# member of the list (indexed [-1]) gets us the most recent one.
	inputFileName = os.listdir(inputDir)[-1]

	file = open(inputDir + '/' + inputFileName)
	next(file) #skip header

	# Due to possible irregularities in the argos output for long foreign addresses,
	# the file must be cleaned to make sure that every record is indeed on a single
	# line.
	lines = []

	for line in file:
		if line[0] == '8': 
			lines.append(line.strip())
		else:
			lines[-1] += line.strip()

	file.close()

	# Now that the file is a list of lines we go through each one and use regex
	# black magic to replace all the commas that are *outside* the quote marks
	# with tabs (it's a positive lookahead if you need to google it)

	studentDataName = './data/student_data.dat'

	out = open(studentDataName, 'w+')
	for line in lines:
		tabLine = re.sub(r'(?=(([^"]*"){2})*[^"]*$),', '	', line)
		out.write(tabLine+'\n')
	out.close()

	# now that we've written the data to student_data.dat, we
	# re-open it in read-only mode.
	studentData = open(studentDataName, 'r')

	finalOutput = open('./OCLC-ready ' + inputFileName[:-4] + '.txt', 'w+')
	finalOutput.write('	'.join(outputFields) + '\n')

	for line in studentData:
		contents = line.split('	') #create list of tab-separated values
		contents = [val.strip('"\n') for val in contents] #remove quote marks

		#match input fields 1->1 with values from list and turn into a dict
		patrondata = dict(zip(inputFields, contents))

		#pull out idAtSource from first half of email field by splitting at @
		patrondata['idAtSource'] = patrondata['emailAddress'].split('@')[0]

		#these are the same for everyone
		patrondata['institutionId'] = '648'
		patrondata['sourceSystem'] = 'urn:mace:oclc:idm:stetson:cas'
		patrondata['borrowerCategory'] = 'Student'
		patrondata['homeBranch'] = '196771'
		patrondata['oclcExpirationDate'] = oclcExpirationDate

		#insert dashes into barcodes
		barcode = patrondata['barcode']
		patrondata['barcode'] = barcode[:3] + '-' + barcode[3:5] + '-' + barcode[5:]
		
		# This goes through the list of output fields and, if they exist in the
		# patrondata, extracts them at the appropriate length.
		oclcRowList = [extractField(field, patrondata) for field in outputFields]
		oclcRow = '	'.join(oclcRowList) #that's a tab
		finalOutput.write(oclcRow + '\n')
	finalOutput.close()
	studentData.close()
except:
	warn = Tk()
	messagebox.showwarning("Warning: Data Error",
						   "This box means something went wrong. Please check\n" +
						   "that the input file is correctly formatted and in\n" +
						   "the input folder. Make sure every line in the\n" +
						   "file has the correct number of fields (even if\n" +
						   "some are empty). Remove all other files from the\n" +
						   "input folder except the newest one. If nothing seems \n" +
						   "wrong with the input then find someone who knows \n" +
						   "Python and has a lot of free time on their hands.")
	warn.quit()
