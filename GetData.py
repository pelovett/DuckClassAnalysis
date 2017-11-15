#Created by Peter Lovett
#Built for python 3.6


from lxml import html
import requests 

def main():

    while(True):
        year = input("Please enter the starting year of the academic year you're interested in:")
        year = int(year)
        if(year <= 2017 and year >= 1990):
            break

    data = collect_data(year)
    return

def collect_data(academic_year):
    PAGE_URL_ONE = "http://classes.uoregon.edu/pls/prod/hwskdhnt.P_ListCrse?term_in="
    PAGE_URL_TWO = "01&submit_btn=Show%20Classes&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummydummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_cred=dummy&sel_tuition=dummy&sel_open=dummy&sel_weekend=&sel_ptrm=&sel_schd=&sel_day=&sel_sess=&sel_instr=&sel_to_cred=&sel_from_cred=&sel_insm=&sel_subj=%25&sel_crse=&sel_crn=&sel_title=&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a&sel_levl=%25&sel_camp=%25&sel_attr=%25&sel_day=&sel_day=&cidx="



    page = requests.get(PAGE_URL_ONE + str(academic_year) + PAGE_URL_TWO + "100")
    tree = html.fromstring(page.content)

    
    MY_QUERY = "//table[@class='datadisplaytable' and @width=600]"

    table = tree.xpath(MY_QUERY)

    #print(table)
    
    QUERY_2 = "//tbody"

    tRows = table[0].xpath(QUERY_2)

    print(len(tRows))
    #print(table[0].getparent())
    
    #All rows but the first are part of the table
    table_data = table[0].getchildren()[1:]

    insideClass = 0
    gradeOpt = ""
    for row in table_data:
        title = row.getchildren()[0]
        #Check for header of course offering data
        if title.get("colspan") == "6":
            print(title.getchildren()[0].text)
            #print("CRN  Avail  Max  Time  Day  Location  Instructor")
            insideClass = title.getchildren()[0].text

        #Either an empty row, or grading option row
        if title.get("colspan") == "15":
            if len(title.getchildren()) == 0:
                continue
            if title.getchildren()[0].get("class") == "datadisplaytable":
                grade_opt = title.getchildren()[0].getchildren()[0]
                grade_opt = grade_opt.getchildren()[1]
                #print(grade_opt.text)
                #TODO finish changing print statements to class instantiations
                
        #A row with a section's information
        if title.get("rowspan") == "1":
            if title.get("width") == "60":
                data_results = ""
                cols = row.getchildren()
                #Lecture, discussion, or Null
                if cols[0].getchildren():
                    #If lecture or discussion
                    data_results += cols[0].getchildren()[0].text
                else:
                    #If Null
                    data_results += cols[0].text+" "
                #CRN
                try:
                    data_results += cols[1].getchildren()[0].text+" "
                except IndexError:
                    print(cols[1])
                    print(cols[1].getchildren())
                if cols[2].getchildren():
                    data_results += cols[2].getchildren()[0].getchildren()[0].text+" "
                else:   
                    #Available seats
                    data_results += cols[2].text+" "
                    #Total seats
                    data_results += cols[3].text+" "
                #Day
                data_results += cols[4].text+" "
                #Location 
                data_results += cols[5].text+" "
                #Instructor
                data_results += cols[6].text+" "
                #Last row is notes we can ignore it for now
                print(data_results)
            
            #Case where there are two listed instructors for one CRN
            elif(title.get("width") == "110"):
                print(row.getchildren()[0].text)

        if title.get("rowspan") == "2":
            print("test rowspan 2 detection")
        


if __name__ == "__main__":
    main()
