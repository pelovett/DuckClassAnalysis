#Created by Peter Lovett
#Built for python 3.6


from lxml import html
import requests 
import numpy as np
from pathlib import Path
from threading import Thread
from queue import Queue

def main():

    while(True):
        loadSave = input("Do you have a saved file (Y/N)?:")
        if(loadSave == "N" or loadSave == "n"):
            break
        if(loadSave == "Y" or loadSave == "y"):
            return load_data()

    while(True):
        year = input("Please enter the starting year of the academic year you're interested in (1990-2017) or all:")
        if(year == "all"):
            data = collect_all_data()
            fileString = Path("data/classDataAll.npy")
            break 
            
        year = int(year)
        if(year <= 2017 and year >= 1990):
            data = collect_data(year)
            fileString = Path("data/classData"+str(year)+".npy")
            break
           
    
    if not fileString.is_file():
        np.save(fileString, data)
    return data

def load_data():
    while(True):
        year = input("Please enter the year of your data file (1990-2017 or all):")
        if(year == "all"):
            return np.load("data/classDataAll.npy")
            
        year = int(year)
        if(year <= 2017 and year >= 1990):
            return np.load("data/classData"+str(year)+".npy")

    

def collect_all_data():
    data = []
    
    class download_worker(Thread):
        def __init__(self, queue, reposit):
            Thread.__init__(self)
            self.queue = queue
            self.reposit = reposit
            
        def run(self):
            while not self.queue.empty():
                year = self.queue.get()
                class_info = collect_data(year)
                self.reposit.append(class_info)
                self.queue.task_done()
    
    years = [x for x in range(1990, 2017)]
    year_queue = Queue()
    for y in years:
        year_queue.put(y)
        
    for i in range(10):
        worker = download_worker(year_queue, data)
        worker.daemon = True
        worker.start()

    year_queue.join()
    final = []
    for year in data:
        for row in year:
            final.append(np.array(row))

    return np.array(final)

def collect_data(academic_year):
    URL_ONE = "http://classes.uoregon.edu/pls/prod/hwskdhnt.P_ListCrse?term_in="
    URL_TWO = "&submit_btn=Show%20Classes&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummydummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_cred=dummy&sel_tuition=dummy&sel_open=dummy&sel_weekend=&sel_ptrm=&sel_schd=&sel_day=&sel_sess=&sel_instr=&sel_to_cred=&sel_from_cred=&sel_insm=&sel_subj=%25&sel_crse=&sel_crn=&sel_title=&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a&sel_levl=%25&sel_camp=%25&sel_attr=%25&sel_day=&sel_day=&cidx="
    terms = ["01", "02", "03"] #Fall, Winter, Spring, respectively
    result_array = []
    
    print("Starting download of year: "+str(academic_year))
    for term in terms:
        #increment by hundreds until we reach end
        increment = 0

        while(True):
            increment += 100
            page = requests.get(URL_ONE+str(academic_year)+term+URL_TWO+str(increment))
            tree = html.fromstring(page.content)

            
            MY_QUERY = "//table[@class='datadisplaytable' and @width=600]"

            table = tree.xpath(MY_QUERY)
            
            QUERY_2 = "//tbody"

            tRows = table[0].xpath(QUERY_2)
            
            #All rows but the first are part of the table
            table_data = table[0].getchildren()[1:]

            #Check if this page is empty
            if(table_data[0].getchildren()[0].text == "No classes were found that meet your search criteria"):
                break


            insideClass = 0
            gradeOpt = ""
            for row in table_data:
                title = row.getchildren()[0]
                #Check for header of course offering data
                if title.get("colspan") == "6":
                    #print("CRN  Avail  Max  Time  Day  Location  Instructor")
                    #Now all rows below this are offered sections of this course
                    title_text = title.getchildren()[0].text
                    title_text = title_text.strip("\xa0").split(" ")
                    insideClass = title_text

                #Either an empty row, or grading option row
                if title.get("colspan") == "15":
                    if len(title.getchildren()) == 0:
                        continue
                    if title.getchildren()[0].get("class") == "datadisplaytable":
                        grade_opt = title.getchildren()[0].getchildren()[0]
                        grade_opt = grade_opt.getchildren()[1].text[1:-1]
                        
                        if(grade_opt == "Optional for all students"):
                            grade_opt = "Opt"
                        elif(grade_opt == "Pass/No Pass Only for all students"):
                            grade_opt = "PNP"
                        elif(grade_opt == "Graded for Majors;\nOptional for all other students"):
                            grade_opt = "Maj"
                        else:
                            grade_opt = "Other: " + grade_opt
                        #Now all rows below this will inherit this grading policy

                #A row with a section's information
                if title.get("rowspan") == "1":
                    if title.get("width") == "60":
                        data_results = []
                        cols = row.getchildren()
                        #Lecture, discussion, or Null
                        if cols[0].getchildren():
                            #If lecture or discussion
                            if(cols[0].getchildren()[0].text == "+ Dis"):
                                data_results.append("Discussion")
                            elif(cols[0].getchildren()[0].text == "+ Lab"):
                                data_results.append("Lab")
                            else:
                                data_results.append(cols[0].getchildren()[0].text)
                        else:
                            #If Null
                            data_results.append('Lecture')
                        #CRN
                        try:
                            data_results.append(cols[1].getchildren()[0].text)
                        except IndexError:
                            print(cols[1])
                            print(cols[1].getchildren())
                        
                        if cols[2].getchildren():
                            continue
                            data_results.append(cols[2].getchildren()[0].getchildren()[0].text+" ")
                            #print(cols[2].getchildren()[0].getchildren()[0].text)
                        else:   
                            #Available seats
                            data_results.append(cols[2].text)
                            #Total seats
                            data_results.append(cols[3].text)
                        #Day
                        data_results.append(cols[4].text)
                        #Location 
                        data_results.append(cols[5].text)
                        #Instructor
                        data_results.append(cols[6].text)
                        #Last row is notes we can ignore it for now

                        data_results.append(grade_opt)  #Grading Option
                        data_results.append(insideClass[0]) #School
                        data_results.append(insideClass[1]) #Class Number
                        data_results.append(term)       #Term offered
                        data_results.append(academic_year)
                        result_array.append(data_results)
                
            #Case where there are two listed instructors for one CRN
            """
            elif(title.get("width") == "110"):
                print(row.getchildren()[0].text)
            """
    return np.array(result_array)
        


if __name__ == "__main__":
    main()
