import requests
import os
from datetime import date, datetime, timedelta
from getpass import getpass
from time import sleep
import json
from urllib.parse import urlencode
import re

if os.name == "nt":
    CLEAR_STR = "cls" 
else:
    CLEAR_STR = "clear"



def clear():
    os.system(CLEAR_STR)

def add_days(date_str,delta):
    date_str = get_date(date_str) + timedelta(days=delta)
    return date_str.strftime("%d/%m/%Y")

def get_date(date_str):
    return date(*[ int(d) for d in date_str.split("/")][::-1])

def makequery(personal_data, booking_data, click, iddoc):

    pd = personal_data
    bd = booking_data

    sched = bd['hours']

    name = personal_data["name"]
    surname = personal_data["surname"]
    CF = personal_data["CF"]

    query_form = {
        "__Click":f"{click}",
        "%%Surrogate_codiceedificio":"1",
        "codiceedificio":f"{bd['building']}",
        "%%Surrogate_aula":"1",
        "aula":f"{bd['classroom']} -- {bd['siram']}",
        "%%Surrogate_selezsettimana":"1",
        "selezsettimana":f"{bd['week']}",
        "%%Surrogate_dalleore1":"1",
        "dalleore1":f"{sched['lun'][0]}",
        "%%Surrogate_alleore1":"1",
        "alleore1":f"{sched['lun'][1]}",
        "%%Surrogate_dalleore2":"1",
        "dalleore2":f"{sched['mar'][0]}",
        "%%Surrogate_alleore2":"1",
        "alleore2":f"{sched['mar'][1]}",
        "%%Surrogate_dalleore3":"1",
        "dalleore3":f"{sched['mer'][0]}",
        "%%Surrogate_alleore3":"1",
        "alleore3":f"{sched['mer'][1]}",
        "%%Surrogate_dalleore4":"1",
        "dalleore4":f"{sched['gio'][0]}",
        "%%Surrogate_alleore4":"1",
        "alleore4":f"{sched['gio'][1]}",
        "%%Surrogate_dalleore5":"1",
        "dalleore5":f"{sched['ven'][0]}",
        "%%Surrogate_alleore5":"1",
        "alleore5":f"{sched['ven'][1]}",
        "%%Surrogate_dalleore6":"1",
        "dalleore6":f"{sched['sab'][0]}",
        "%%Surrogate_alleore6":"1",
        "alleore6":f"{sched['sab'][1]}",
        "%%Surrogate_dichiarazione":"1",
        "dichiarazione":":",
        "database":"prenotazioni/prenotaaule.nsf",
        "ruolodomino":"$$WebClient",
        "utente":f"{pd['matricola']}",
        "form":"prenotaposto-in-aula",
        "ruolo":"studente",
        "iddoc":f"{iddoc}",
        "cancella":"",
        "recorddeleted":"",
        "SaveOptions":"0",
        "matricola":f"{pd['matricola']}",
        "codicefiscale":f"{pd['CF']}",
        #"datanasc":"",
        "numerobadge":"",
        "corsodistudio":"",
        "cognome":f"{surname}",
        "nome":f"{name}",
        "codicecorso":"",
        "email":f"{pd['email']}",
        "facolta":"",
        "nuovo_documento":"0",
        "fila":"",
        "posto":"",
        "seriale":"",
        "codicesiram":f"{bd['siram']}",
        "webdb":"/prenotazioni/prenotaaule.nsf/",
        "Message":"",
        "cancellato":"NO",
        "flag":"0",
        "controllomatricole":f"{pd['range-mat']}#{bd['week']}",
        "numerosettimane":"",
        "appo":f"{bd['week']}#",
        "directoryaule":"prenotazioni/prenotaaule.nsf",
        "directory":"prenotazioni",
        "servername":"prodigit.uniroma1.it",
        "appo22":"",
        "systemreaders":"[admin]",
        "userreaders":f"uid={pd['matricola']}/ou=students/ou=users/dc=uniroma1/dc=it",
        "prenotaappo":"SI",
        "controllomatr":f"{bd['week']}#",
        "indirizzo":f"{bd['addr']}",
        "ubicazione":f"{bd['street-addr']}",
        "data1":f"{bd['week']}",
        "data2":f"{add_days(bd['week'],1)}",
        "data3":f"{add_days(bd['week'],2)}",
        "data4":f"{add_days(bd['week'],3)}",
        "data5":f"{add_days(bd['week'],4)}",
        "data6":f"{add_days(bd['week'],5)}",
        "$$HTMLFrontMatter":"<!DOCTYPE html>",
        "$$HTMLTagAttributes":"lang=\"it\"",
        "httpcookie":"1"
    }
    
    res = urlencode(query_form)

    return res


# Returns next weekday "day" after the date "date". day=0 => monday, day=6 => sunday
def next_weekday(date, day=0):
    return date + timedelta(days=(day-date.weekday()+7)%7)


# format some fields of a booking_data dictionary
def _format_bd(data):
    global siram_codes, addresses, classrooms

    try:
        if data['classroom'] not in classrooms[data['building']]:
            print(f"\nError: unlisted classroom \"{data['classroom']}\" in {data['building']}, be sure to use the EXACT same name used in Prodigit")
            input("\nPress Enter to exit")
            close()
        else:
            siram = siram_codes[data["building"]+"#"+data["classroom"]]
    except KeyError:
        print(f"\nError: unlisted building code \"{data['building']}\" in {data['building']}, be sure to use the EXACT same name used in Prodigit")
        input("\nPress Enter to exit")
        close()


    days = set(["lun", "mar", "mer", "gio", "ven", "sab"]) # TODO: MON TUE WED THU FRI SAT ?
    for day in data["hours"]:
        days -= set([day])
        # if hours are uncorrectly settled, this changes them to default. Last if condition is to avoid "10:--" and similar
        from_h = data["hours"][day][0]
        to_h = data["hours"][day][1]
        if from_h == "" or from_h == ":" or (not ":" in from_h) or ("--" in from_h):
            data["hours"][day][0] = "--:--"
            data["hours"][day][1] = "--:--"
            continue
        if to_h == "" or to_h == ":" or (not ":" in to_h) or ("--" in to_h):
            data["hours"][day][0] = "--:--"
            data["hours"][day][1] = "--:--"

    # completing remaining days if not present. 
    # TODO: ordering the data[hours] entries by day? it is not needed but I will consider 
    for day in list(days):
        data["hours"][day] = ["--:--", "--:--"]

    # Set Siram code
    data["siram"] = siram

    # Set the week data to next monday
    today = date.today()
    data["week"] = next_weekday(today).strftime("%d/%m/%Y")

    # Set the building complex name and street-address if present on the boudling-info.json list   
    data["addr"] = addresses[data["building"]]["addr"]
    data["street-addr"]= addresses[data["building"]]["street-addr"]
        


# format some fields of a personal_data dictionary
def _format_pd(data):
    if data["range-mat"] == "":
        mat = data["matricola"]
        data["range-mat"] = str(round(float("0."+mat[-2:]))*50)+"-"+str(round(float("0."+mat[-2:]))*50+49)

    if data["email"] == "":
        data["email"] = f"{data['surname'].lower()}.{data['matricola']}@studenti.uniroma1.it"


def close(timesl=1):
    # close the program
    os.system(CLEAR_STR)
    print("\n\n\n           Bye         ,(è >è)/\n\n\n")
    sleep(timesl)
    os.system(CLEAR_STR)
    exit()


def void_req(s, personal_data, iddoc ):
    book = {
            "classroom": "AULA A3",
            "building": "RM102",
            "week": "25/10/2021",
            "siram": "RM102-E01PR1L008",
            "hours": {
                "lun": [
                    "--:--",
                    "--:--"
                ],
                "mar": [
                    "--:--",
                    "--:--"
                ],
                "mer": [
                    "--:--",
                    "--:--"
                ],
                "gio": [
                    "--:--",
                    "--:--"
                ],
                "ven": [
                    "--:--",
                    "--:--"
                ],
                "sab": [
                    "--:--",
                    "--:--"
                ]
            },
            "addr": "",
            "street-addr": ""
        }
    r = s.post(book_url, data=makequery(personal_data, book, click="$Refresh", iddoc=iddoc), timeout=5)
    return r


# Retrieves some session and user data
def get_data(s):

    try:
        r = s.get(book_url, timeout=5)
        #print(r.text)
        #input()
    except requests.exceptions.RequestException as e:
        print(f"\nError in connection with Prodigit\n")
        print(e)

    click_mark = "\_doClick\(\'[^$][^\']+\'\,"
    m = re.search(click_mark, r.text)
    if m is not None:
        click = m.group(0)[10:-2]
        #print(f"Click: {click}")
        #click = click[:-4]+"1EEE"
        #print(f"Click: {click}")
    else:
        print(f"\nError in retrieving data from Prodigit\n")
        input("\n\nPress Enter to exit\n\n")
        close()


    cf_mark = "<input name=\"codicefiscale\" type=\"hidden\" value=\"[^\"]+"
    m = re.search(cf_mark, r.text)
    if m is not None:
        cf = m.group(0)[49:]
        #print(f"CF: {cf}")
    else:
        print(f"\nError in retrieving data from Prodigit\n")
        if personal_data["CF"] == "":
            input("\n\nPress Enter to exit\n\n")
            close()


    iddoc_mark = "<input name=\"iddoc\" type=\"hidden\" value=\"[^\"]+"
    m = re.search(iddoc_mark, r.text)
    if m is not None:
        iddoc = m.group(0)[41:]
        #print(f"iddoc: {iddoc}")
    else:
        print(f"\nError in retrieving data from Prodigit\n")
        input("\n\nPress Enter to exit\n\n")
        close()

    surname_mark = "<input name=\"cognome\" type=\"hidden\" value=\"[^\"]+"
    m = re.search(surname_mark, r.text)
    if m is not None:
        surname = m.group(0)[43:]
        #print(f"Surname: {surname}")
    else:
        print(f"\nError in retrieving data from Prodigit\n")
        input("\n\nPress Enter to exit\n\n")
        close()

    name_mark = "<input name=\"nome\" type=\"hidden\" value=\"[^\"]+"
    m = re.search(name_mark, r.text)
    if m is not None:
        name = m.group(0)[40:]
        #print(f"Name: {name}")
    else:
        print(f"\nError in retrieving data from Prodigit\n")
        input("\n\nPress Enter to exit\n\n")
        close()

    per_data = {      
        "CF": cf,
        "name": name,
        "surname": surname,
    }

    _format_pd2(personal_data, per_data)
    r = void_req(s, personal_data, iddoc)
    click_mark = "\_doClick\(\'[^$][^\']+\'\,"
    m = re.search(click_mark, r.text)
    if m is not None:
        click = m.group(0)[10:-2]
        #print(f"\nClick: {click}")
    else:
        print(f"\nError in retrieving data from Prodigit\n")
        input("\n\nPress Enter to exit\n\n")
        close()

    active_mark = "Le prenotazioni delle aule per le lezioni non sono attive"
    if active_mark in r.text:
        active = False
        #print(r.text)
        #input()
    else:
        active = True

    data = {
        "click": click,
        "CF": cf,
        "iddoc": iddoc,
        "active": active,
        "name": name,
        "surname": surname,
    }

    return data
    

# format some fields of a personal_data dictionary
def _format_pd2(personal_data, s_data):

    mat = personal_data["matricola"]
    personal_data["range-mat"] = str(round(float("0."+mat[-2:]))*50)+"-"+str(round(float("0."+mat[-2:]))*50+49)

    personal_data["email"] = f"{s_data['surname'].lower()}.{personal_data['matricola']}@studenti.uniroma1.it"

    personal_data["surname"] = s_data["surname"]
    personal_data["name"] = s_data["name"]
    personal_data["CF"] = s_data["CF"]


booking_dict = {
            "classroom": "",
            "building": "",
            "hours": {
                "lun": [
                    "--:--",
                    "--:--"
                ],
                "mar": [
                    "--:--",
                    "--:--"
                ],
                "mer": [
                    "--:--",
                    "--:--"
                ],
                "gio": [
                    "--:--",
                    "--:--"
                ],
                "ven": [
                    "--:--",
                    "--:--"
                ],
                "sab": [
                    "--:--",
                    "--:--"
                ]
            }
        }

if __name__=="__main__":

    clear()

    json_file_name = "config.json"
    buildings_info_json = "buildings-info.json"
    SLEEP_TIME = 0.5
    

    with open(json_file_name, "r") as jfile:
        config_data = json.load(jfile)

    with open(buildings_info_json, "r") as jfile:
        buildings_info = json.load(jfile)

    personal_data = config_data["personal_data"]
    bookings = config_data["booking_list"]
    siram_codes = buildings_info["siram_codes"]
    addresses = buildings_info["addresses"]
    class_list = buildings_info["classrooms"]
    buildings_list = buildings_info["buildings"]

    
    classrooms = {}
    for key in siram_codes:
        classrooms[key.split("#")[0]]=[]
    for key in siram_codes:
        classrooms[key.split("#")[0]].append(key.split("#")[1])


    url = "https://prodigit.uniroma1.it"
    book_url = "https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula?"
    
    # User Agent
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    headers = {'User-Agent': user_agent}



    login_data = {
        "Username": personal_data["matricola"],
        "Password": personal_data["password"]
    }


    user_not_setted = login_data['Username'] == ""
    if user_not_setted:
        login_data['Username'] = input("\nMatricola: ").strip()
    else:
        print(f"\nMatricola: {login_data['Username']}")

    pass_not_setted = login_data['Password'] == ""
    if pass_not_setted: 
        login_data["Password"] = getpass("Password: ")
        #login_data["Password"] = input("Password: ") # if you prefer to not hide password entry
        clear()


    with requests.Session() as s:
        s.headers.update(headers)
        # Login
        try:
            clear()
            r = s.post(url+"/names.nsf?Login", data=login_data, timeout=5)
            #print(r.text)
            if "Autenticazione non effettuata" in r.text:
                print("\nAccess Failed\n")               
                input("\n\nPress Enter to exit\n\n")
                close()
            else:
                print("\nLogged in!")
            input("\n\nPress Enter to start booking\n\n")
        except requests.exceptions.RequestException as e:
                print(f"\nError in Login\n")
                print(e)


        # Retrieving some session and user data
        s_data = get_data(s) 
        # format data
        _format_pd2(personal_data, s_data)

        # Checking booking availability. Not avaible for now since not stable
        '''
        if not s_data["active"]:
            clear()
            print("\n\n    ,(t.t),(t.t),(t.t),(t.t),(t.t),(t.t),\n    ,(t.t),                       ,(t.t),\n    ,(t.t), Booking not available ,(t.t),\n    ,(t.t),                       ,(t.t),\n    ,(t.t),(t.t),(t.t),(t.t),(t.t),(t.t),")
            #print("\nBooking not available ,(t.t),")
            input("\n\nPress Enter to exit\n\n")
            close()
        '''

        # Bookings
        for booking_data in bookings:
            try:
                if booking_data["classroom"] == "" or booking_data["building"] == "":
                    continue
                clear()
                _format_bd(booking_data)
                r = s.post(book_url, data=makequery(personal_data, booking_data, click=s_data["click"], iddoc=s_data["iddoc"]), timeout=5)
                #print(makequery(personal_data, booking_data, click=s_data["click"], iddoc=s_data["iddoc"]))
                #print("\n\n\n\n")
                #print(r.text)
                #input()
                
                if "PRENOTAZIONI EFFETTUATE" in r.text:
                    print(f"\nReservation successfully made for {booking_data['classroom']} at {booking_data['building']}\n")

                elif "Sovrapposizione in data" in r.text:
                    print(f"\nReservation already (or partially) present for {booking_data['classroom']} at {booking_data['building']}\n")

                else:
                    print(f"\nError in reservation for {booking_data['classroom']} at {booking_data['building']}\n")

                sleep(SLEEP_TIME)
            except requests.exceptions.RequestException as e:
                print(f"\nError in reservation\n")
                print(e)


    input("\n\nPress Enter to exit\n\n")
    close()







