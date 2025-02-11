from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import *
from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup as soup
import re
from urllib.error import HTTPError
from urllib.error import URLError
from time import sleep
import threading
import sys

app = QtWidgets.QApplication ([])
dlg = uic.loadUi ("okScraper.ui")
startCal = QtWidgets.QCalendarWidget ()
startCal.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
startCal.setGridVisible (True)
stopCal = QtWidgets.QCalendarWidget ()
stopCal.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
stopCal.setGridVisible (True)
startURL = "https://okcountyrecords.com"

def grabCounties():
    try:
        url = "https://okcountyrecords.com/site-list"
        request = Request(url, headers = {'User-Agent' :\
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"})
        uClient = urlopen (request)
        page_html = uClient.read ()
        uClient.close ()

        pageSoup = soup (page_html, 'html.parser')
        pageSoup = pageSoup.body.tbody

        for tr in pageSoup.find_all('tr'):
            county = str(tr.find('td').find('span'))
            county = county[21:-14]
            if (len (county) > 0):
                dlg.countyComboBox.addItem(county)
    except:
        QMessageBox.about (dlg, "Network Error", "Cannot access okcountyrecords.com.  Check your network connection and try again.")
        dlg.countyComboBox.setEnabled (False)
        pass

def toggleButtons(setBool, clear=True):
    if clear == True:
        dlg.instrumentComboBox.clear()
        dlg.sectionComboBox.clear()
        dlg.townshipComboBox.clear()
        dlg.rangeComboBox.clear()
        dlg.instrumentComboBox.addItem("Instrument Type")
        dlg.sectionComboBox.addItem("Section")
        dlg.townshipComboBox.addItem("Township")
        dlg.rangeComboBox.addItem("Range")
        dlg.startDateButton.setText("Start Date")
        dlg.stopDateButton.setText("Stop Date")
 
    dlg.instrumentComboBox.setEnabled(setBool)
    dlg.sectionComboBox.setEnabled(setBool)
    dlg.townshipComboBox.setEnabled(setBool)
    dlg.rangeComboBox.setEnabled(setBool)
    dlg.startDateButton.setEnabled(setBool)
    dlg.stopDateButton.setEnabled(setBool)

def setSearchParams ():
    instrument = dlg.instrumentComboBox.currentText ()
    township = dlg.townshipComboBox.currentText ()
    rangee = dlg.rangeComboBox.currentText ()
    section = dlg.sectionComboBox.currentText ()

    if not instrument == "Instrument Type" or not township == "Township" or not section == "Section" or not rangee == "Range":
        dlg.scrapeButton.setEnabled (True)
    else:
        dlg.scrapeButton.setEnabled (False)

def grabComboItems ():
    county = dlg.countyComboBox.currentText()

    if county == "County":
        toggleButtons(False, clear = True)
        dlg.instrumentComboBox.setEditable (False)
        dlg.townshipComboBox.setEditable (False)
        dlg.sectionComboBox.setEditable (False)
        dlg.rangeComboBox.setEditable (False)
    else:
        try:
            toggleButtons(True, clear = True)
            url = "https://okcountyrecords.com/search/" + county.replace(" ", "+")
            request = Request(url, headers = {'User-Agent' :\
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"})
            uClient = urlopen (request)
            page_html = uClient.read ()
            uClient.close ()

            pageSoup = soup (page_html, 'html.parser')
            instrumentSoup = pageSoup.body.find_all('dd')[4].find_all('option')
            sectionSoup = pageSoup.body.find_all('dd')[9].find_all('option')
            townshipSoup = pageSoup.body.find_all('dd')[10].find_all('option')
            rangeSoup = pageSoup.body.find_all('dd')[11].find_all('option')

            for instrument in instrumentSoup:
                matches=re.findall(r'\=\"(.+?)\"\>',str(instrument))
                if len(matches) > 0:
                    dlg.instrumentComboBox.addItem(re.sub('amp;', '', str(matches[0])))
            if dlg.instrumentComboBox.count () < 2:
                dlg.instrumentComboBox.setEditable (True)
                dlg.instrumentComboBox.clear ()
                dlg.instrumentComboBox.addItem ("Type Instrument Here")
            else:
                dlg.instrumentComboBox.setEditable (False)

            
            for section in sectionSoup:
                matches=re.findall(r'\=\"(.+?)\"\>',str(section))
                if len(matches) > 0:
                    dlg.sectionComboBox.addItem(str(matches[0]))
            if dlg.sectionComboBox.count () < 2:
                dlg.sectionComboBox.setEditable (True)
                dlg.sectionComboBox.clear ()
                dlg.sectionComboBox.addItem ("Type Section")
            else:
                dlg.sectionComboBox.setEditable (False)

            for township in townshipSoup:
                matches=re.findall(r'\=\"(.+?)\"\>',str(township))
                if len(matches) > 0:
                    if not str(matches[0])[-1] == ".":
                        dlg.townshipComboBox.addItem(str(matches[0]))
            if dlg.townshipComboBox.count () < 2:
                dlg.townshipComboBox.setEditable (True)
                dlg.townshipComboBox.clear ()
                dlg.townshipComboBox.addItem ("Type Township")
            else:
                dlg.townshipComboBox.setEditable (False)

            for rangee in rangeSoup:
                matches=re.findall(r'\=\"(.+?)\"\>',str(rangee))
                if len(matches) > 0:
                    if not str(matches[0])[-1] == "." and not str(matches[0])[0] == "0":
                        dlg.rangeComboBox.addItem(str(matches[0]))
            if dlg.rangeComboBox.count () < 2:
                dlg.rangeComboBox.setEditable (True)
                dlg.rangeComboBox.clear ()
                dlg.rangeComboBox.addItem ("Type Range")
            else:
                dlg.townshipComboBox.setEditable (False)

            toggleButtons(True, clear=False)
        except:
            QMessageBox.about (dlg, "Network Error", "Cannot access okcountyrecords.com.  Check your network connection and try again.")
            pass

def openCal (title):
    toggleButtons (False, clear=False)
    dlg.countyComboBox.setEnabled(False)
    if title == "Select Start Date":
        startCal.show()
        startCal.setWindowTitle(title)
    elif title == "Select Stop Date":
        stopCal.show()
        stopCal.setWindowTitle(title)

def closeCal(title):
    toggleButtons (True, clear=False)
    dlg.countyComboBox.setEnabled(True)
    if title == "start":
        startCal.hide ()
        startDate = str (startCal.selectedDate ().toPyDate ())
        dlg.startDateButton.setText ("Start: " + startDate)
    if title == "stop":
        stopCal.hide ()
        stopDate = str (stopCal.selectedDate ().toPyDate ())
        dlg.stopDateButton.setText ("Stop: " + stopDate)
    
def startScrapeThread(url, county):
    # make url into a list of len=1 to pass into the thread
    urList = [url]
    global scrapeThread
    scrapeThread = threading.Thread(target=scrape, args=(urList, county))
    scrapeThread.daemon = True
    scrapeThread.start()

def stopScrapeThread ():
    global cancelButtonFlag
    cancelButtonFlag = True

def setConnects ():
    # grab county
    county = dlg.countyComboBox.currentText()
    dlg.countyComboBox.currentIndexChanged.connect (grabComboItems)
    dlg.instrumentComboBox.currentIndexChanged.connect (setSearchParams)
    dlg.townshipComboBox.currentIndexChanged.connect (setSearchParams)
    dlg.rangeComboBox.currentIndexChanged.connect (setSearchParams)
    dlg.sectionComboBox.currentIndexChanged.connect (setSearchParams)
    dlg.startDateButton.clicked.connect (lambda: openCal("Select Start Date"))
    dlg.stopDateButton.clicked.connect (lambda: openCal("Select Stop Date"))
    startCal.selectionChanged.connect (lambda: closeCal('start'))
    stopCal.selectionChanged.connect (lambda: closeCal('stop'))
    dlg.scrapeButton.clicked.connect (lambda: startScrapeThread (startURL, county))

def scrape (baseURL, county):
    # Set buttons to the 'scraping state'
    toggleButtons(False, clear=False)
    dlg.countyComboBox.setEnabled(False)
    dlg.scrapeButton.setEnabled(False)

    # Create url from baseURL and data in combo boxes
    baseURL = makeURL(baseURL[0])
    url = baseURL + "/page-1"
    try:
        # Pretend we're a web browser
        request = Request(url, headers = {'User-Agent' :\
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"})
        uClient = urlopen (request)
        page_html = uClient.read ()
        uClient.close ()

        pageSoup = soup (page_html, "html.parser")
        pageSoup = pageSoup.body

        # find out how many pages of results there are and obtain that number
        pagination = pageSoup.find ("nav", {"class":"pagination"})
        pageList = str(pagination)
        try:
            pageList = pageList.split("\n",7)[-2]
        except:
            QMessageBox.about (dlg, "Form Error", "Make sure you spelled everything correctly in the forms and try agian.")
            sys.exit ()
        result = re.search("/page-(.*)<", str(pageList))
        almostThere = result.group(1)
        pageTotal = ""
        for char in almostThere:
            if char.isdigit ():
                pageTotal += char
                continue
            else:
                break
        pageTotal = int(pageTotal) + 1

        # Initialize the working page numbers and data entry number
        workingPage = 1
        dataTableEntryNumber = 1

        # For each page in the list of pages that we just pulled, go through
        for page in range(1, pageTotal + 1):
            if page == 0:
                continue
            else:
                url = baseURL + "/page-" + str (workingPage)

                # Pretend we're a web browser and open the current page of results
                request = Request(url, headers = {'User-Agent' :\
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"})
                uClient = urlopen (request)
                page_html = uClient.read ()
                uClient.close ()
                
                pageTag = soup (page_html, "html.parser")
                pageTag = pageTag.body.tbody

                # for each result in the result page, go to that result and pull data
                for i in pageTag:
                    i = i.a
                    i = str(i)

                    i = re.search("href=\"(.*)\">", i)
                    i = i.group (1)

                    url = "https://okcountyrecords.com" + i

                    # Pretend we're a web browser and open next result from result page
                    request = Request(url, headers = {'User-Agent' :\
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"})
                    uClient = urlopen (request)
                    page_html = uClient.read ()
                    uClient.close ()

                    # Program has reached the destination page for desired data
                    finalPage = soup (page_html, "html.parser")

                    # find all data fields in the table that contains the desired data
                    tables = finalPage.find_all('table')
                    for tbl in tables:
                        if tbl == tables[0]:
                            tds = tbl.findChildren ('td')
                        else:
                            tds += tbl.findChildren ('td')

                    # TODO: Add better handling here.  could result in shifted CSV rows if any of these data are missing.

                    # Grab the book data and place it in the table along with the county
                    book = re.search(">(.*)</td>", str(tds[0]))
                    book = book.group (1)
                    if book:
                        currentRowCount = dlg.dataTable.rowCount() #necessary even when there are no rows in the table
                        dlg.dataTable.insertRow(currentRowCount)
                        dlg.dataTable.setItem(currentRowCount, 0, QTableWidgetItem(dlg.countyComboBox.currentText ()))
                        dlg.dataTable.setItem(currentRowCount, 1, QTableWidgetItem(book))

                    # Grab the page data and place it in the table
                    page = re.search(">(.*)</td>", str(tds[1]))
                    page = page.group (1)
                    if page:
                        dlg.dataTable.setItem(currentRowCount, 2, QTableWidgetItem(page))

                    # Grab the instrument data and place it in the table
                    instrument = re.search("heavy\">(.*)</td>", str(tds[2]))
                    instrument = instrument.group (1)
                    if instrument:
                        dlg.dataTable.setItem(currentRowCount, 3, QTableWidgetItem(instrument))

                    # Grab the document stamps data and place it in the table
                    documentStamps = re.search("<td>(.*)</td>", str(tds[6]))
                    documentStamps = documentStamps.group (1)
                    if documentStamps:
                        dlg.dataTable.setItem(currentRowCount, 4, QTableWidgetItem(documentStamps))

                    # Grab the recorded on data and place it in the table
                    recordedOn = re.search ("<td>(.*)</td>", str(tds[7]))
                    recordedOn = recordedOn.group (1)
                    if recordedOn:
                        dlg.dataTable.setItem(currentRowCount, 5, QTableWidgetItem(recordedOn))

                    # Grab the instrument date data and place it in the table
                    if len(tds) > 8:
                        instrumentDate = re.search ("<td>(.*)</td>", str(tds[8]))
                        instrumentDate = instrumentDate.group (1)
                    else:
                        instrumentDate = ""
                    if instrumentDate:
                        dlg.dataTable.setItem(currentRowCount, 6, QTableWidgetItem(instrumentDate))
                        
                        dlg.dataTable.setItem(currentRowCount, 7, QTableWidgetItem(url))

                    # delay so we don't overwhelm the web servers and get blocked or something
                    sleep (.5)

                    # Set the scrape counter value
                    dlg.rowCounter.display(dataTableEntryNumber)

                    # Increment row number for data table
                    dataTableEntryNumber += 1

                # increment page number to go to next page
                workingPage += 1
                
    except HTTPError:
        QMessageBox.about (dlg, "Http Error", "Cannot access okcountyrecords.com.  Check your network connection and try again.")
    except URLError:
        QMessageBox.about (dlg, "URL Error", "Cannot access okcountyrecords.com.  Check your network connection and try again.")

def makeURL (url):
    url += "/results/"
    
    if not dlg.instrumentComboBox.currentText () == "Instrument Type":
        instrumentFlag = True
        url += "instrument-type={}:".format (dlg.instrumentComboBox.currentText ().replace (" ", "+"))
    else:
        instrumentFlag = False 
    if not dlg.startDateButton.text () == "Start Date":
        url += "recorded-start={}:".format (dlg.startDateButton.text ()[-10:])
    if not dlg.stopDateButton.text () == "Stop Date":
        url += "recorded-end={}:".format (dlg.stopDateButton.text ()[-10:])
    if not dlg.sectionComboBox.currentText () == "Section":
        sectionFlag = True
        url += "section={}:".format (dlg.sectionComboBox.currentText ().replace (" ", "+"))
    else:
        sectionFlag = False
    if not dlg.townshipComboBox.currentText () == "Township":
        townshipFlag = True
        url += "township={}:".format (dlg.townshipComboBox.currentText ().replace (" ", "+"))
    else:
        townshipFlag = False
    if not dlg.rangeComboBox.currentText () == "Range":
        rangeFlag = True
        url += "range={}:".format (dlg.rangeComboBox.currentText ().replace (" ", "+"))
    else:
        rangeFlag = False

    if not instrumentFlag and not sectionFlag and not townshipFlag and not rangeFlag:
        QMessageBox.about (dlg, "Selection Error", "Must select more info to scrape!")
        return "error"
    else:
        url += "site={}".format (dlg.countyComboBox.currentText ().replace (" ", "+"))
        # print (url)
        return url

def main ():
    grabCounties ()
    setConnects ()
    dlg.show()
    app.exec_()

if __name__ == "__main__":
    main ()