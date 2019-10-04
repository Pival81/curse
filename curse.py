import requests
import json as JSON
from threading import Thread
import operator
from urllib import parse
from pyqt_browser_2 import Main


""" class CustomEncoder(JSON.JSONEncoder):
 
     def default(self, o):
 
         return {'__{}__'.format(o.__class__.__name__): o.__dict__} """

""" 
Sort:
Featured = 0
Popularity = 1
Last Updated = 2
Name = 3
Author = 4
Total Downloads = 5 """

class Mod():

	def __init__(self, modlist_manager=None, id=None, json=None):
		self.headers = {"User-Agent": "CurseClient/7.5 (Microsoft Windows NT 6.1.7600.0) CurseClient/7.5.7208.4378"}
		self.mainUrl = "https://addons-ecs.forgesvc.net"
		self.modlist_manager = modlist_manager
		if id:
			self.id = id
			self.json = JSON.loads(requests.get(self.mainUrl + "/api/v2/addon/" + str(self.id), headers=self.headers).text)
		else:
			self.json = json
			self.id = self.json["id"]
		self.url = self.json["websiteUrl"]
		self.name = self.json["name"]
		self.summary = self.json["summary"]
		self.categories = [i["name"] for i in self.json["categories"]]
		#self.description = self.getHTMLCorrected(self.mainUrl + "/v2/addon/" + str(self.id) + "/description")
		del self.json

	def getHTMLCorrected(self, url):
		import bs4
		html = requests.get(url, headers=self.headers)
		soup_obj = bs4.BeautifulSoup(html.text, 'lxml')
		links = soup_obj.find_all('a')
		for link in links:
			if link.get("href") and link.get("href").startswith("/linkout?remoteUrl="):
				link["href"] = link["href"].replace("/linkout?remoteUrl=", "")
				link["href"] = parse.unquote(parse.unquote(link["href"]))
		return str(soup_obj)

	def getFiles(self):
		filelist_json = requests.get(self.mainUrl + "/api/v2/addon/" + str(self.id) + "/files", headers=self.headers)
		self.filelist = JSON.loads(filelist_json.text)
		self.filelist.sort(key=operator.itemgetter('fileDate'), reverse=True)

	def update(self, gameVers, path, releasetype="release"):
		if releasetype == "release":	checkReleaseType = [1]
		elif releasetype == "beta":	checkReleaseType = [1, 2]
		elif releasetype == "alpha":	checkReleaseType = [1, 2, 3]
		for file in self.filelist:
			if gameVers in file["gameVersion"] and file["releaseType"] in checkReleaseType:
				if self.modlist_manager.checkFile(self.id, file["id"]):
					self.installFile(file["downloadUrl"], file["fileName"], file["id"], path)
				break

	def install(self, gameVers, path, releasetype="release", ask=True):
		if releasetype == "release":	checkReleaseType = [1]
		elif releasetype == "beta":	checkReleaseType = [1, 2]
		elif releasetype == "alpha":	checkReleaseType = [1, 2, 3]
		rlsTypes = ["Release", "Beta", "Alpha"]

		filelistVers = []
		idx = 1
		for file in self.filelist:
			if not ask:
				if idx<6 and gameVers in file["gameVersion"] and file["releaseType"] in checkReleaseType:
					for dependency in file["dependencies"]:
						if dependency["type"] == 3:
							mod = Mod(modlist_manager=self.modlist_manager, id=dependency["addonId"])
							mod.getFiles()
							if self.modlist_manager.checkMod(mod.id):
								mod.update(gameVers, path, releasetype)
							else:
								mod.install(gameVers, path, releasetype, ask)
					if self.modlist_manager.checkFile(self.id, file["id"]):
						self.installFile(file["downloadUrl"], file["fileName"], file["id"], path, [item["addonId"] for item in file["dependencies"] if item["type"] == 3])
						return None
			
			if idx<6 and gameVers in file["gameVersion"] and file["releaseType"] in checkReleaseType:
				print(idx, rlsTypes[file["releaseType"]-1], file["displayName"], file["fileName"])
				print("-----------------------------")
				filelistVers.append(file)
				idx = idx + 1
		try:
			fileSelected = int(input(">>")) - 1
		except:
			buh = Main(self.id)
		for dependency in filelistVers[fileSelected]["dependencies"]:
			if dependency["type"] == 3:
				mod = Mod(modlist_manager=self.modlist_manager, id=dependency["addonId"])
				mod.getFiles()
				if self.modlist_manager.checkMod(mod.id):
					mod.update(gameVers, path, releasetype)
				else:
					mod.install(gameVers, path, releasetype)
		if self.modlist_manager.checkFile(self.id, filelistVers[fileSelected]["id"]):
			self.installFile(filelistVers[fileSelected]["downloadUrl"], filelistVers[fileSelected]["fileName"], filelistVers[fileSelected]["id"], path, [item["addonId"] for item in filelistVers[fileSelected]["dependencies"] if item["type"] == 3])
	
	def installFile(self, url, filename, fileid, path, dependencies=[]):
		self.modlist_manager.removeMod(self.id, removeDependents=False)
		file = requests.get(url, headers=self.headers)
		with open(path + "/.minecraft/mods/" + filename, "wb") as f:
			f.write(file.content)
		self.modlist_manager.addMod(self.id, fileid, filename, dependencies)
		print("Installed", filename)

class ModList():

	def __init__(self, path):
		self.path = path
		self.open()

	def addMod(self, id, fileid, filename, dependencies):
		if self.checkFile(id, fileid):
			self.modlist.append({"id": id, "fileid": fileid, "filename": filename, "dependencies": dependencies})
		else:
			print("File", filename, "is already installed")
			exit()
		self.close()

	def checkMod(self, id):
		self.open()
		for item in self.modlist:
			if item["id"] == id:
				return True
		return False

	def checkFile(self, id, fileid):
		self.open()
		for item in self.modlist:
			if item["id"] == id and item["fileid"] == fileid:
				return False
		return True
	
	def removeMod(self, id, removeDependents=True):
		for item in self.modlist:
			if item["id"] == id:
				if removeDependents:
					for i in [i["id"] for i in self.modlist if id in i["dependencies"]]:
						self.removeMod(i)
				import os
				os.remove(self.path + "/.minecraft/mods/" + item["filename"])
				print("Removed", item["filename"])
				self.modlist.remove(item)
		self.close()
	
	def open(self):
		try:
			with open(self.path + "/modlist.json", "r") as modlist_file:
				self.modlist = JSON.load(modlist_file)
		except:
			self.modlist = []

	def close(self):
		with open(self.path + "/modlist.json", "w+") as modlist_file:
			JSON.dump(self.modlist, modlist_file, indent=4)

class Curse():


	def __init__(self, path):
		self.mainUrl = "https://addons-ecs.forgesvc.net"
		self.modlist_manager = ModList(path)
		self.headers={"User-Agent": "CurseClient/7.5 (Microsoft Windows NT 6.1.7600.0) CurseClient/7.5.7208.4378"}

	""" def showDescription(url):
		import sys
		from pyqt_browser_2 import RestrictedWebViewWidget
		from PyQt5 import QtWidgets 

		app = QtWidgets.QApplication(sys.argv)
		web = RestrictedWebViewWidget(url=url)
		web.show()
		app.exec_() """

	def updateModpack(self, gameVers, path, releasetype):
		for entry in self.modlist_manager.modlist:
			mod = Mod(modlist_manager=self.modlist_manager, id=entry["id"])
			mod.getFiles()
			print("Checking {}".format(mod.name))
			mod.update(gameVers, path, releasetype)

	def getModList(self, arg, gameVers, itemPerPage, sort):
		index = 0
		flag = True
		modlist_final = []
		if arg == "":
			exit()
		while(flag):
			modlist = requests.get( self.mainUrl + "/api/v2/addon/search?categoryId=0&gameId=432" +
			"&gameVersion=" + gameVers +
			"&index=" + str(index) +
			"&pageSize=" + itemPerPage +
			"&searchFilter=" + parse.quote(arg) + 
			"&sectionId=6&sort=" + sort
			, headers=self.headers)
			modlist = JSON.loads(modlist.text)
			for i, x in enumerate(modlist):
				modlist_final.append(Mod(modlist_manager=self.modlist_manager, json=x))
			if len(modlist) != int(itemPerPage):
				flag = False
			index = index + int(itemPerPage)
		""" 
		with open("mods.json", "w") as json_file:
			json_file.write(JSON.dumps(modlist_final, indent=4, sort_keys=True, separators=(',', ': '), cls=CustomEncoder)) """
		
		return modlist_final


if __name__ == "__main__":
	curse = Curse()
	curse.getModList(input(">>"), "1.12.2", "25", "0")
