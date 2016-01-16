import os, sys, sqlite3, shutil, datetime

def main(sourceFilename, destFilename):
	print(sourceFilename)
	print(destFilename)
	sourceConn = sqlite3.connect(sourceFilename)
	destConn = sqlite3.connect(destFilename)
	
	# Backup the destination database
	shutil.copy(destFilename, destFilename + "." + str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) + ".backup")

	sourceCursor = sourceConn.cursor()
	destCursor = destConn.cursor()
	# Movies
	# http://kodi.wiki/view/Databases#movieview
	for row in sourceCursor.execute("SELECT c00, c09, playCount, lastPlayed, dateAdded FROM movieview WHERE playCount IS NOT NULL"):
		#print("Watched", row[0])
		numInDest = destCursor.execute("SELECT COUNT(*) FROM movie_view WHERE c09=?", (row[1],)).fetchone()[0]
		if numInDest == 0:
			print("Couldn't find movie", row[0], "in destination DB")
		elif numInDest > 1:
			print("Multiple movies with name", row[0], "in destination DB!! Existing")
			sys.exit(1)
		else:
			print("Updating", row[0])
			destIdFile = destCursor.execute("SELECT idFile FROM movie_view WHERE c09=?", (row[1],)).fetchone()[0]
			destCursor.execute("UPDATE files SET playCount=?, lastPlayed=?, dateAdded=? WHERE idFile=?", (row[2], row[3], row[4], destIdFile))

	# TV Shows (episodes)
	# http://kodi.wiki/view/Databases#episodeview
	for row in sourceCursor.execute("SELECT strFilename, playCount, lastPlayed, dateAdded FROM episodeview WHERE lastPlayed IS NOT NULL"):
		numInDest = destCursor.execute("SELECT COUNT(*) FROM files WHERE strFilename=?", (row[0],)).fetchone()[0]
		if numInDest == 0:
			print("Couldn't find TV episode", row[0], "in destination DB")
		elif numInDest > 1:
			print("Multiple TV episodes with name", row[0], "in destination DB!! Existing")
			sys.exit(1)
		else:
			print("Updating", row[0])
			destCursor.execute("UPDATE files SET playCount=?, lastPlayed=?, dateAdded=? WHERE strFilename=?", (row[1], row[2], row[3], row[0]))

	sourceConn.close()
	destConn.close()


if (__name__ == '__main__'):
	main(sys.argv[1], sys.argv[2])