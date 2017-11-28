#Created by Peter Lovett
#Built for python 3.6


from lxml import html
import requests 
import numpy as np

def main():

    while(True):
        loadSave = input("Do you have a saved file (Y/N)?:")
        if(loadSave == "N" or loadSave == "n"):
            break
        if(loadSave == "Y" or loadSave == "y"):
            return load_data()

    while(True):
        year = input("Please enter the starting year of the academic year you're interested in (1990-2017):")
        year = int(year)
        if(year <= 2017 and year >= 1990):
            break
           
    data = collect_data(year)
    fileString = "data/classData"+str(year)+".npy"
    np.save(fileString, data)
    return data

def load_data():
    while(True):
        year = input("Please enter the year of your data file (1990-2017):")
        year = int(year)
        if(year <= 2017 and year >= 1990):
            break

    return np.load("data/classData"+str(year)+".npy")

def collect_data(academic_year):
    PAGE_URL_ONE = "http://classes.uoregon.edu/pls/prod/hwskdhnt.P_ListCrse?term_in="
    PAGE_URL_TWO = "01&submit_btn=Show%20Classes&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummydummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_cred=dummy&sel_tuition=dummy&sel_open=dummy&sel_weekend=&sel_ptrm=&sel_schd=&sel_day=&sel_sess=&sel_instr=&sel_to_cred=&sel_from_cred=&sel_insm=&sel_subj=%25&sel_crse=&sel_crn=&sel_title=&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a&sel_levl=%25&sel_camp=%25&sel_attr=%25&sel_day=&sel_day=&cidx="
    result_array = []

    #increment by hundreds until we reach end
    increment = 0

    while(True):
        increment += 100
        page = requests.get(PAGE_URL_ONE+str(academic_year)+PAGE_URL_TWO+str(increment))
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

                    data_results.append(grade_opt)
                    data_results.append(insideClass[0])
                    data_results.append(insideClass[1])
                    
                    result_array.append(data_results)
                
            #Case where there are two listed instructors for one CRN
            """
            elif(title.get("width") == "110"):
                print(row.getchildren()[0].text)
            """
    return np.array(result_array)
        


if __name__ == "__main__":
    main()
