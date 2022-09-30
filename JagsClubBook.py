import datetime as dt
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


def main():
    # print ('hello world')

    # create a dictionary of classes that i want to book
    # <option value="J3CLACYC1940082">Advanced Cyclefit</option>
    # <option value="J6CLCT10100820">Cardio Tone</option>
    # <option value="J2CLCIC18100820">Circuits</option>
    # <option value="J7CLCYC09100820">Cyclecore</option>
    # <option value="J5CLREY18100820">Restorative Yoga (friday)</option>
    # <option value="J7CLYOG10100820">Yoga (sunday)</option>

    # Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
    # dict_classes = {2: ['Advanced Cyclefit'], 5:['Cardio Tone'], 1:["Circuits"], 6:["Cyclecore","Yoga (sunday)"]}
    # 21 Apr 21 outdoor classes are now has folloiwng collection:
    # <option value="J2CLCATO1910032">Cardio Tone 7.10pm</option>
    # <option value="J6CLCAT10100321">Cardio Tone 10.10am</option>
    # <option value="J2CLCIR18100321">Circuits 6.10pm</option>

    # dict_classes = {0: ["Circuits - Mon 6pm", "Yoga (mon 7.10pm)"], 1: ["Cardio Tone", "Cyclecross"],
    #                 2: ['Hot Yoga - Wed 7pm'], 3: ["Boot Camp - Thurs 6.45am"], 4: ["Hot Yoga - Fri 6.15pm"],
    #                 5: ['Cardio Tone - Sat 10.10am'], 6: ["Cyclecore", "Yoga"]}

    # dict_classes = {0: ["Circuits - Mon 6pm", "Yoga (mon 7.10pm)"], 1: ["Cardio Tone", "Cyclecross"],
    #                 2: ['Hot Yoga - Wed 7pm'], 3: ["Boot Camp - Thurs 6.45am"], 4: ["Hot Yoga - Fri 6.15pm"],
    #                 5: ['Cardio Tone - Sat 10.10am'], 6: ["Cyclecore"]}

    # dict_classes = {0: ["Circuits - Mon 6pm"], 1: ["Cyclecross"],
    #                 2: ['Hot Yoga - Wed 7pm'], 3: ["Boot Camp - Thurs 6.45am"], 4: ["Hot Yoga - Fri 6.15pm"],
    #                 5: ['Cardio Tone - Sat 10.10am'], 6: ["Cyclecore","Yoga"]}

    # changed 13 Mar 22
    # dict_classes = {0: ["Circuits - Mon 6pm"], 1: ["Cyclecross"],
    #                 2: ['Hot Yoga - Wed 7pm'], 3: ["Boot Camp - Thurs 6.45am"], 4: ["Hot Yoga - Fri 6.15pm"],
    #                 5: ['Cardio Tone - Sat 10.10am'], 6: ["Cyclecore", "Enduran Cyclefit Sun 8am"]}

    # changed 27 Aug 22
    dict_classes = {0: ["Circuits - Mon 6pm", "Trx - Mon 6pm"], 1: ["Cyclecross"],
                    2: ['Hot Yoga - Wed 7pm'], 3: ["Boot Camp - Thurs 6.45am"], 4: ["Hot Yoga - Fri 6.15pm"],
                    5: ['Cardio Tone - Sat 10.10am']}

    driver = webdriver.Chrome('D:\Downloads\Programming\chromedriver.exe')

    # port = 50603
    # s = Service('D:\Downloads\Programming\chromedriver.exe')
    # driver = webdriver.Chrome(service=s)
    # op = webdriver.ChromeOptions()
    # op.add_argument("--headless")
    # op.add_argument("--disable-gpu")
    # capabilities = op.to_capabilities()
    # # driver = webdriver.Chrome(service=ser, options=op, port=50603)
    # # driver = webdriver.Chrome(port, op, ser)
    # driver = webdriver.Chrome(service_args=ser, options=op,  desired_capabilities=capabilities)


    homePage = 'https://bookings.jagssportsclub.co.uk/Connect/memberHomePage.aspx'
    loginPage = 'https://bookings.jagssportsclub.co.uk/Connect/MRMLogin.aspx'

    driver.get(loginPage)

    # time.sleep(2)  # Let the user actually see something!

    # driver.find_element_by_id("ctl00_MainContent_InputLogin").send_keys("119424")
    # driver.find_element_by_id("ctl00_MainContent_InputPassword").send_keys("9416")
    # driver.find_element_by_id("ctl00_MainContent_btnLogin").click()

    driver.find_element(By.ID, "ctl00_MainContent_InputLogin").send_keys("119424")
    driver.find_element(By.ID, "ctl00_MainContent_InputPassword").send_keys("9416")
    driver.find_element(By.ID, "ctl00_MainContent_btnLogin").click()

    # set date and query dict
    # create a datetimeobjects, then convert it to date
    dtObj = dt.datetime.today()
    fdate = dt.date(dtObj.year, dtObj.month, dtObj.day)
    # fdate = fdate+dt.timedelta(days=1)
    # set from-date, with current bookings, all classes get booked 7 days in advance, so script needs to run for lookout on 7days time
    frmDate = fdate
    # frmDate = fdate + dt.timedelta(days=7)
    # set to-date
    # toDate =fdate +  dt.timedelta(days=3), keep to-Date same as From-Date
    toDate = fdate + dt.timedelta(days=7)
    # toDate =frmDate

    print(fdate.weekday())
    wkday = fdate.weekday()
    frmWkDay = frmDate.weekday()
    toWkDay = toDate.weekday()
    # wkday = int(input('provide a number to retrieve class for that day: '))
    # clsthatday = dict_classes.get(fdate.weekday())

    frmDate = dt.datetime.strftime(frmDate, '%d-%m-%Y')
    toDate = dt.datetime.strftime(toDate, '%d-%m-%Y')

    try:  # do all processing here
        print(dict_classes[wkday])
        act2book = dict_classes[wkday]

        print(frmDate, '-', toDate, '-', frmWkDay, '-', toWkDay)

        for i in [frmWkDay, toWkDay]:
            szl = len(dict_classes[i])
            print(dict_classes[i], '-', szl)
            if szl >= 1:
                for j in range(0, szl):
                    print(list(dict_classes.get(i))[j], '-', 'i=', i, '-', 'j=', j)
                    actElem = list(dict_classes.get(i))[j]
                    # check if you get more than 1 value 
                    # click to get the advanced search menu displayed
                    driver.find_element(By.XPATH,
                                        "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[1]/h3").click()
                    time.sleep(1)

                    # set the activity type = classes
                    # s2 = Select(driver.find_element_by_xpath(
                    #     "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div/div/div[2]/select"))
                    # s2 = Select(driver.find_element_by_xpath(
                    #     "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div/div/div[2]/select"))

                    # 19Apr21 = selection of outdoor classes
                    # < option
                    # value = "OS CLASSES" > Outdoor
                    # Classes < / option >
                    # /html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div/div/div[2]/select/option[7]
                    s2 = Select(driver.find_element(By.XPATH,
                                                    "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div/div/div[2]/select"))
                    s2.select_by_index(0)
                    time.sleep(2)

                    # now set the activity review the list below  = <option value="J3CLACYC1940082">Advanced Cyclefit</option>
                    # < option
                    # value = "J6CLCAT10100321" > Cardio
                    # Tone
                    # 10.10
                    # am < / option >
                    # /html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[3]/div/div/div/div[2]/select/option[2]

                    s2 = Select(driver.find_element(By.XPATH,
                                                    '/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[3]/div/div/div/div[2]/select'))
                    # s2.select_by_value("J3CLACYC1940082")
                    # s2.select_by_visible_text("Advanced Cyclefit")
                    # s2.select_by_visible_text("Any")
                    # Iterate through the dictionary for the right classes for the day
                    s2.select_by_visible_text(actElem)

                    # set from and to dates in the datepicker fields
                    time.sleep(2)

                    # From Date
                    # s1 = driver.find_element_by_xpath("/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[4]/div/div/div[1]/input").send_keys("24092020")
                    print(frmDate, '-', toDate, '-', frmWkDay, '-', toWkDay)
                    s1 = driver.find_element(By.XPATH,
                                             "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[4]/div/div/div[1]/input").send_keys(
                        frmDate)
                    time.sleep(1)
                    # driver.implicitly_wait(5)

                    # to date
                    # s4=driver.find_element_by_xpath("/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[5]/div/div/div[1]/input").send_keys("29092020")

                    s4 = driver.find_element(By.XPATH,
                                             "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[5]/div/div/div[1]/input").send_keys(
                        toDate)
                    time.sleep(3)
                    # driver.implicitly_wait(5)

                    # press search button now
                    driver.find_element(By.ID, "ctl00_MainContent__advanceSearchUserControl__searchBtn").click()

                    # get entire accordian
                    # actlist = driver.find_element(By.XPATH,
                    #     "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[3]/div/div/div[1]/div[2]")
                    # print(len(actlist))
                    # # for i in actlist:
                    # #     print (i)

                    # put implicit wait get the link text test then click
                    time.sleep(3)
                    driver.implicitly_wait(10)
                    # driver.find_element_by_link_text("Kundalini Yoga").click()
                    try:
                        driver.find_element(By.LINK_TEXT, actElem).click()
                    except NoSuchElementException:
                        print(
                            'Got no booking available exception Going back to search page-No results were found that match your search')
                        driver.get(homePage)
                    except ElementClickInterceptedException:
                        print(
                            'Element clicked but no results- Got no booking available exception Going back to search page-No results were found that match your search')
                        time.sleep(5)  # Let the user actually see something!
                        driver.get(homePage)

                        # now book as you in the booking screen
                    # check if you can book ie button is clickable otherwise try another activity
                    # //*[@id="ctl00_MainContent_ClassStatus_ctrl0_btnBook"]
                    # button-ActivityID=J7CLCYC09100820 ResourceID=10365172 Duration=50 Status=No Space & No Waiting List Date=27/09/2020 09:10:00
                    driver.implicitly_wait(5)
                    try:
                        # driver.find_element_by_partial_link_text("Status=No Space & No Waiting List Date").click()
                        # /html/body/form/div[3]/div/div/div/section/div/div[2]/div[1]/div[5]/div[2]/table/tbody/tr[1]/td/input
                        # //*[@id="ctl00_MainContent_ClassStatus_ctrl0_btnBook"]
                        # Sorry, no available activities could be found, or you are already booked into this activity.

                        driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ClassStatus_ctrl0_btnBook"]').click()
                        time.sleep(1)


                        # takes to the next screen you have to confirm book again 
                        # //*[@id="ctl00_MainContent_btnBasket"]

                        driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_btnBasket"]').click()

                        # then you have to go back to main home screen
                        # http://bookings.jagssportsclub.co.uk/Connect/memberHomePage.aspx

                        time.sleep(5)  # Let the user actually see something!

                        driver.get(homePage)



                    except ElementClickInterceptedException:
                        print(
                            'Trying to Click - Got no booking available exception Going back to search page-No results were found that match your search')
                        driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ClassStatus_ctrl1_btnBook"]').click()
                        # takes to the next screen you have to confirm book again
                        # //*[@id="ctl00_MainContent_btnBasket"]

                        driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_btnBasket"]').click()

                        time.sleep(5)  # Let the user actually see something!
                        driver.get(homePage)
                    except NoSuchElementException:
                        print(
                            'No Eleement in booking - Got no booking available exception Going back to search page-No results were found that match your search')
                        time.sleep(5)  # Let the user actually see something!
                        driver.get(homePage)

                        # if booking for only 1 day clasesses not range, no need to run the for loop again for toWkDay
            if frmWkDay == toWkDay:
                break




    except KeyError:
        print("No Class to be booked today")

    time.sleep(5)  # Let the user actually see something!
    driver.quit()


if __name__ == "__main__":
    main()
