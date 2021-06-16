import pandas_datareader as data
import datetime
import matplotlib.pyplot as plt
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from matplotlib.pyplot import figure
import mplfinance as mpf


def main_menu():
    next_step = '1'
    while next_step == '1':
        WelcomeMessage = str(input('''
----------------------------------------
Welcome to Carpark Slot Checker!
 
Please select a function to continue:
1. Check your desinated carpark availability
2. Check carpark number using address
3. View volume of available slots for past 12 hours
4. Exit Program
 
 
(sample input : 1 or 2 or 3)
'''))

        if WelcomeMessage == '1':
            next_step = availability()
        elif WelcomeMessage == '2':
            next_step = carparknumber()
        elif WelcomeMessage == '3':
            next_step = graph()
        elif WelcomeMessage == '4':
            print('Thank you for using!')
            next_step = '2'
        else:
            print('Please provide correct option!')
            next_step = '2'
            main_menu()


# Check availale slots. Option 1
def availability():
    flag = False

    while flag == False:

        ##initialising, get data from api
        url = 'https://api.data.gov.sg/v1/transport/carpark-availability'
        result = requests.get(url)
        jsonStr = result.json()

        ##extract items as a list from the dict in api
        items = jsonStr.get("items")

        ##extract carpark_data as a list from the dict in items
        carpark_data = items[0]["carpark_data"]

        ##traverse and return the sub-list(checker_list) with matched carpark number in carpark_data list
        ##extract all the data in the nested list and dict
        ##There are 3 keys in the dict in carpark_data list: carpark_info, carpark_number, update_datetime
        input_number = str(input('''

------------Availlable Slots------------

Please key in your carpark code:____
(sample input:Y28M)
'''))
        checker_list = list(filter(lambda number: number['carpark_number'] == input_number.upper(), carpark_data))

        ##check for invalid input or wrong car park number
        ##ask to do again if invalid or wrong

        if not checker_list:
            print('The carpark number dose not exist!')
            print('\n')
            choice_checker_list_empty = str(input('''
Would you like to try again?
1.Yes
2.No
'''))
            if choice_checker_list_empty == '1':
                availability()
            else:
                break

        else:
            ##extract from checker_list layer
            checker_list_carpark_info = checker_list[0]["carpark_info"]
            checker_list_carpark_number = checker_list[0]["carpark_number"]

            ##extract from checker_list_carpark_info layer
            total_lots = checker_list_carpark_info[0]["total_lots"]
            lot_type = checker_list_carpark_info[0]["lot_type"]
            lots_available = checker_list_carpark_info[0]["lots_available"]

            ##extract date and time separatedly to string, which will be printed out in results for clearer view.
            checker_list_datetime = checker_list[0]["update_datetime"]
            checker_list_datetime = checker_list_datetime.split('T')
            date, time = checker_list_datetime

            print('-----------------RESULT-----------------\n')
            print('Your carpark number: ', checker_list_carpark_number)
            print('Date:', date, '\nTime: ', time)
            print('Total slots: ', total_lots, '\n')
            print('Available slots: ', lots_available)
            print('\n------------------END-------------------')

            flag = True

    next_step = next_request()

    return next_step


##Check car park number. Option 2
def carparknumber():
    pd.set_option('display.max_rows', 100)

    flag = False
    while flag == False:

        input_keyword = str(input('''
----------Carpark number check----------
Please input address:
'''))
        ##info stored in local csv file
        ##traverse and match with user input

        raw_data = pd.read_csv('carparkinfo.csv')
        raw_data = raw_data[['car_park_no', 'address']]
        selected = raw_data[raw_data['address'].str.lower().str.contains(input_keyword)]
        selected = selected.set_index('address')
        total_results = int(selected.count())

        ##deal with different circumstances

        ##ask to do again if input does not match

        if selected.empty:
            print('There is no carpark match your address!')
            choice_empty = str(input('''
Would you like to try again?
1.Yes
2.No
'''))
            if choice_empty == '1':

                carparknumber()

            elif choice_empty == '2':
                print('\n------------------END-------------------\n')
                break

        ##ask to do again if too many results/not precised

        elif total_results > 99:
            print('-----------------RESULT-----------------\n')
            print('Please provide a more specific address!')
            print('\n------------------END-------------------')
            choice_total_results = str(input('''
Would you like to try again?
1.Yes
2.No
'''))
            if choice_total_results == '1':

                carparknumber()
                break


            else:
                print('\n------------------END-------------------')

                break

        ##if everything is fine, give output
        else:
            print('-----------------RESULT-----------------\n')
            print(selected)
            print('\n------------------END-------------------')
            break

    next_step = next_request()
    return next_step


##Draw volume graph for past 12 hours. Option 3
def graph():
    url = 'https://api.data.gov.sg/v1/transport/carpark-availability'
    input_number = str(input('''
------------------Graph-----------------

Please key in your carpark code:____
(sample input:Y28M)
'''))

    ##Initialise the two lists for drawing graph later

    timelist = []
    slotlist = []

    ##use loop to store time and number of slots in the two lists.
    ##used try except to avoid invalid input

    try:
        for i in range(13, -1, -1):
            datetime1 = datetime.now() - timedelta(hours=i)
            datetime2 = datetime1.strftime('%Y-%m-%dT%H:%M:%S')
            slotlist.append(slot(input_number, datetime2))
            timelist.append(datetime1.strftime('%d-%H:%M'))

        figure(figsize=(15, 8))
        plt.axis([1, 14, 0, 15])
        bar_width = 0.5
        plt.bar(timelist, slotlist, bar_width, color='g')
        plt.title('Number of available lots')
        plt.xlabel('Date-Time')
        plt.ylabel('Slots')
        plt.show()
        next_step = next_request()
        return next_step

    ##if invalid input, ask whether want to do again
    except:
        print("Please provide correct car park number!")

        choice_wrongnumber = str(input('''
Would you like to try again?
1.Yes
2.No
'''))
        if choice_wrongnumber == '1':
            carparknumber()
        else:
            print('\n------------------END-------------------\n')
            next_step = next_request()
            return next_step


##slot() is for outputting available slots with provided date and time
##modified based on availability() function
##will be used in graph() function
def slot(input_number, datetime2):
    url = 'https://api.data.gov.sg/v1/transport/carpark-availability'
    result = requests.get(url,
                          params={'date_time': datetime2})
    jsonStr = result.json()

    items = jsonStr.get("items")

    carpark_data = items[0]["carpark_data"]

    checker_list = list(filter(lambda number: number['carpark_number'] == input_number.upper(), carpark_data))
    checker_list_carpark_info = checker_list[0]["carpark_info"]

    total_lots = checker_list_carpark_info[0]["total_lots"]
    lot_type = checker_list_carpark_info[0]["lot_type"]
    lots_available = checker_list_carpark_info[0]["lots_available"]

    checker_list_carpark_number = checker_list[0]["carpark_number"]

    return lots_available


##to trigger next action, direct to main menu or exit.
def next_request():
    next_word = '''
Would you like to
1. return to menu
2. exit program
(sample input : 1 or 2)
'''

    next_step = str(input(next_word))

    return next_step


main_menu()
