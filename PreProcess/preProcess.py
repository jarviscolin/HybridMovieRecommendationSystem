def preProcess(os,utils,random,DE_EFFECT,userMovieRating,LAPTOP_TEST,\
               PROCESS_MOVIE_TAG,PROCESS_SOCIAL,PROCESS_HISTORY):
    
#-----------------------------------------------------------------
# Reads in data file with (userID, movieID, rating) format.
# Removes duplicates
# Randomizes the ordering
# Splits data into training_set and crossVal_set files according to
#   the specification in utils.DATA_SET_SPLIT
# De-effects
# Makes a prediction text with a "dummy" rating for libfm
# Saves in Data/PreProcessed/training_set_processed.txt
# and Data/PreProcessed/predict_dummy.txt
#-----------------------------------------------------------------

    makeDummyPredictions(utils)
    
    cleanUpData(utils.ORIGINAL_DATA_PATH,
                utils.ORIGINAL_DATA_CLEAN_PATH)
    
    if PROCESS_MOVIE_TAG:
        print('... Processing Movie Tag Data')
        processMovieTags(utils)
        
    if PROCESS_SOCIAL:
        print('... Processing User Social Data')
        processSocialData(utils)

    if PROCESS_HISTORY:
        print('... Processing User History Data')
        processHistoryData(utils)

    # De-effects data file
    if DE_EFFECT:
        deEffectData(utils.ORIGINAL_DATA_CLEAN_PATH, \
                 utils.PROCESSED_DATA_PATH, utils,userMovieRating)
    else:
        os.system("cp " + utils.ORIGINAL_DATA_CLEAN_PATH + " " + \
                  utils.PROCESSED_DATA_PATH)
    if LAPTOP_TEST:
        # makes a small data set able to run on laptops
        utils.bootstrap(utils.PROCESSED_DATA_PATH,\
                        utils.PROCESSED_DATA_PATH_TEMP, \
                        10000,random,False)
        os.system('mv '+utils.PROCESSED_DATA_PATH_TEMP+' '+\
                  utils.PROCESSED_DATA_PATH)

def makeDummyPredictions(utils):
#-----------------------------------------------------------------
# Makes dummy 3rd column in prediction file for LibFM
#-----------------------------------------------------------------
    inPredict = open(utils.TEST_IDS_PATH, 'r')
    outPredict = open(utils.TEST_IDS_DUMMY_PATH, 'w')
    for line in inPredict:
        if line != '\n':
            line = line.replace('\n','\t1\n') #adds dummy column
            outPredict.write(line)
    inPredict.close()
    outPredict.close()

def processHistoryData(utils):
#-----------------------------------------------------------------
# Generates a processed user history file that cuts out all the extraneous
#  users who do not rate in the actual training set
#-----------------------------------------------------------------
    historyData = open(utils.USER_HISTORY_PATH, 'r')
    fout = open(utils.PROCESSED_HISTORY ,'w')
    
    # this gets a set of all users and all movies we see in our data set
    userSet=set()
    movieSet=set()
    data = open(utils.ORIGINAL_DATA_PATH,'r')
    for line in data:
        if line != '\n':
            columns = line.split('\t')
            user = columns[0]
            movie = columns[1]
            if user not in userSet:
                userSet.add(user)
            if movie not in movieSet:
                movieSet.add(movie)
    data.close()
    
    historyDict = {}
    usersSeen=set()
    for line in historyData:
        if line != '\n':
            line = line.replace('\n', '')
            columns = line.split('\t')
            user = columns[0]
            if user in userSet:
                if user not in usersSeen:
                    historyDict[user]=[]
                    usersSeen.add(user)
                movie = columns[1]
                if movie in movieSet:
                    historyDict[user].append(movie)
    for user in historyDict:
        string=''
        for movie in historyDict[user]:
            string=string+movie+','
        string=string[:-1]
        fout.write(user+'\t'+string+'\n')
    historyData.close()
    fout.close()
    
def processSocialData(utils):
    import os
#-----------------------------------------------------------------
# Generates a processed social file that cuts out all the extraneous
#  users which do not show up in the actual training set
#-----------------------------------------------------------------
    socialData = open(utils.USER_SOCIAL_PATH, 'r')
    fout = open(utils.PROCESSED_SOCIAL ,'w')
    
    # this gets a set of all users we see in our data set
    userSet=set()
    userData = open(utils.ORIGINAL_DATA_PATH,'r')
    for line in userData:
        if line != '\n':
            columns = line.split('\t')
            user = columns[0]
            if user not in userSet:
                userSet.add(user)
    userData.close()
    
    socialDict = {}
    for line in socialData:
        if line != '\n':
            line = line.replace('\n', '')
            columns = line.split('\t')
            user = columns[0]
            if user in userSet:
                friends = columns[1]
                friendList = friends.split(',')
                string=''
                for friend in friendList:
                    if friend in userSet:
                        string=string+friend+','
                string=string[:-1]
                if string != '':
                    fout.write(user+'\t'+string+'\n')
    fout.close()

def processMovieTags(utils):
    import os
#-----------------------------------------------------------------
# Generates a file from movie_tag.txt that has format
# (movie1, movie2, N) where N is the number of tags they share
#-----------------------------------------------------------------

    # creates dict with movies as keys and list of tags as value
    movieTags = open(utils.MOVIE_TAG_PATH, 'r')
    movieTagDict = {}
    movieList =[]
    movieSet=set()
    lineCount=0
    for line in movieTags:
        if line != '\n':
            line = line.replace('\n', '')
            columns = line.split('\t')
            movie = columns[0]
            movieList.append(movie)
            allTags = columns[1]
            tagList = allTags.split(',')
            if movie not in movieSet:
                movieSet.add(movie)
                movieTagDict[movie]=[]
            for tag in tagList:
                movieTagDict[movie].append(tag)
            lineCount+=1
    movieTags.close()
    
    fout = open(utils.PROCESSED_MOVIE_TAG, 'w')
    linesSq=lineCount**2
    speed =0 # counter
    for i in range(len(movieList)):
        mov1 = movieList[i]
        for j in range(i+1,len(movieList)):
            tagCount = 0
            mov2 = movieList[j]
            for tag1 in movieTagDict[mov1]:
                for tag2 in movieTagDict[mov2]:
                    if tag1 == tag2:
                        tagCount +=1
            if tagCount > 0:
                fout.write(mov1+'\t'+mov2+'\t'+str(tagCount)+'\n')
            
            if speed%50==0:
                os.sys.stdout.write('{0}\r'.format( \
                    str('-- '+str('{0:.2f}'.format(speed/linesSq*100))+\
                        ' percent of data written --')))
            speed+=1
    fout.close()

def cleanUpData(inputPath,outputPath):
#-----------------------------------------------------------------
# Erases empty lines and duplicates, randomizes rows if randomize == True
#-----------------------------------------------------------------
    lines_seen = set() # holds lines already seen
    data = []
    newDataFile = open(outputPath,'w')
    for line in open(inputPath,'r'):
        if line != '\n':
            if line not in lines_seen: # not a duplicate
                lines_seen.add(line)
                newDataFile.write( line )
    newDataFile.close()
            
def deEffectData(infilePath, outfilePath, utils,userMovieRating):

#-----------------------------------------------------------------
# Reads in data file with (userID, movieID, rating) format.
# Saves files containing the average rating for each user, average
#   rating for each movie, and the global average rating.
# Also outputs a 'de-effected' file with format
#   (userID, movieID, newRating) where newRating is the rating
#   subtracted from the global average rating.
#-----------------------------------------------------------------

    infile = open(infilePath, 'r')
    lineCounter= 0
    usersDict = {}  # all ratings by user
    moviesDict = {} # all ratings by movie
    globalSum = 0
    umr = {} # dictionary of movies and ratings by user, saved to utils.userMovieRating
    
    for line in infile:
        if line != '\n':
            lineCounter += 1
            line = line.replace('\n', '')
            columns = line.split('\t')
            user = columns[0]
            movie = columns[1]
            rating = float(columns[2])

            if usersDict.get(user)==None:
                usersDict[user]=[]
            usersDict[user].append(rating)

            if moviesDict.get(movie)==None:
                 moviesDict[movie]=[]
            moviesDict[movie].append(rating)
            
            if user not in umr:
                umr[user]=([movie],[rating])
            elif user in umr:
                umr[user][0].append(movie)
                umr[user][1].append(rating)
    
            
            globalSum += rating
    userMovieRating = umr       
    infile.close()

    globalMean = globalSum/lineCounter

    movieMeanDict = {}  # average rating by movie
    userMeanDict = {}   # average rating by user

    for i in usersDict:
        userMeanDict[i] = listAverager(usersDict.get(i))
        
    for i in moviesDict:
        movieMeanDict[i] = listAverager(moviesDict.get(i))

    # write de-effected data set (each rating +/- the global mean rating)
    infile = open(infilePath, 'r')
    outfile = open(outfilePath, 'w')
    for line in infile:
        line = line.replace('\n', '')
        columns = line.split('\t')
        user = columns[0]
        movie = columns[1]
        newRating = globalMean - float(columns[2])
        outfile.write(user+'\t'+movie+'\t'+ str(newRating)+'\n')
    infile.close()
    outfile.close()

    # write user effect file (average rating by user)
    userFile = open(utils.EFFECTS_USER_PATH, 'w')
    for i in userMeanDict:
        userFile.write(str(i) +'\t'+ str(userMeanDict.get(i)) + '\n')
    userFile.close()
    
    # write movie effect file (average rating by movie)
    movieFile = open(utils.EFFECTS_MOVIE_PATH, 'w')
    for i in movieMeanDict:
        movieFile.write(str(i) +'\t'+ str(movieMeanDict.get(i)) + '\n')
    movieFile.close()

    # write global effect file (global average)
    globalFile = open(utils.EFFECTS_GLOBAL_PATH, 'w')
    globalFile.write(str(globalMean))
    globalFile.close()

def listAverager(ls):

#-----------------------------------------------------------------
# Takes a list of numbers in and returns the average
#-----------------------------------------------------------------

    total = 0
    for i in ls:
        total += i
    return total/len(ls)        
