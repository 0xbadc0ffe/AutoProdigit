import requests
import os
from datetime import date, datetime, timedelta
from getpass import getpass
from time import sleep
import json
from urllib.parse import urlencode

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

def makequery(personal_data, booking_data):

    pd = personal_data
    bd = booking_data

    sched = bd['hours']

    click = "C12585E7003519C8.172ed58cde110161c12585f80042d28d/$Body/1.1EEE"
    iddoc = "3C0137D0723E44F6C1258767005FCAB6"
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
        "numerobadge":"",
        "corsodistudio":"",
        "cognome":f"{pd['surname']}",
        "nome":f"{pd['name']}",
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
        siram = ""
        if data['classroom'] not in classrooms[data['building']]:
            print(f"\nWarning: unlisted classroom \"{data['classroom']}\", be sure to use the EXACT same name used in Prodigit")
        else:
            siram = siram_codes[data["building"]+"#"+data["classroom"]]
    except KeyError:
        print(f"\nWarning: unlisted building code \"{data['building']}\", be sure to use the EXACT same name used in Prodigit")

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

    # If siram not present or different from the right one (if present into the config.json list)
    if data["siram"] == "" or (siram != "" and data["siram"] != siram):
        try:
            data["siram"] = siram
        except KeyError:
            print("\nUnlisted Siram code or wrong classroom/building code")
            print("\nPlease check in the following link and add the correct siram code into cofig.json")
            print("\nhttps://gomp.uniroma1.it/PublicFunctions/GestioneAule/SchedaOrarioProgrammazione.aspx\n")
            input("\n\npress Enter to go on...\n\n")

    # Set the week data to next monday
    today = date.today()
    if data["week"] == "" or get_date(data["week"]) < today:
        data["week"] = next_weekday(today).strftime("%d/%m/%Y")

    # Set the building complex name and street-address if present on the config.json list   
    if data["building"]!="":
        try:
            data["addr"] = addresses[data["building"]]["addr"]
            data["street-addr"]= addresses[data["building"]]["street-addr"]
        except KeyError:
            print(f"\nWarning: unlisted address (bulding complex name) and street address for \"{data['building']}\"")

    '''
    # The previous do not allow to set a different addresses then the real one (if listed)
    # This, instead, allow it.
    if data["addr"] == "" or data["street-addr"] == "" and data["building"]!="":
        try:
            data["addr"] = addresses[data["building"]]["addr"]
            data["street-addr"]= addresses[data["building"]]["street-addr"]
        except KeyError:
            print(f"\nWarning: unlisted address (bulding complex name) and street address for \"{data['building']}\"")
    '''



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


booking_dict = {
            "classroom": "",
            "building": "",
            "week": "",
            "siram": "",
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

if __name__=="__main__":

    clear()

    json_file_name = "config.json"
    SLEEP_TIME = 0.5

    with open(json_file_name, "r") as jfile:
        config_data = json.load(jfile)

    personal_data = config_data["personal_data"]
    bookings = config_data["booking_list"]
    siram_codes = config_data["siram_codes"]
    addresses = config_data["addresses"]

    
    classrooms = {}
    for key in siram_codes:
        classrooms[key.split("#")[0]]=[]
    for key in siram_codes:
        classrooms[key.split("#")[0]].append(key.split("#")[1])


    _format_pd(personal_data)



    url = "https://prodigit.uniroma1.it"
    book_url = "https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula?"



    login_data = {
        "Username": personal_data["matricola"],
        "Password": personal_data["password"]
    }


    pass_not_setted = login_data['Password'] == ""
    if pass_not_setted:
        print(f"\nMatricola: {login_data['Username']}")
        login_data["Password"] = getpass("Password: ")
        #login_data["Password"] = input("Password: ") # if you prefer to not hide password entry
        clear()


    with requests.Session() as s:

        # Login
        try:
            clear()
            r = s.post(url+"/names.nsf?Login", data=login_data, timeout=5)
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

        # Bookings
        for booking_data in bookings:
            try:
                if booking_data["classroom"] == "" or booking_data["building"] == "":
                    continue
                clear()
                _format_bd(booking_data)
                r = s.post(book_url, data=makequery(personal_data,booking_data), timeout=5)
                if "PRENOTAZIONI EFFETTUATE" in r.text:
                    print(f"\nReservation successfully made for {booking_data['classroom']} at {booking_data['building']}\n")

                elif "Sovrapposizione in data" in r.text:
                    print(f"\nReservation already present (or partially) for {booking_data['classroom']} at {booking_data['building']}\n")

                else:
                    print(f"\nError in reservation for {booking_data['classroom']} at {booking_data['building']}\n")

                sleep(SLEEP_TIME)
            except requests.exceptions.RequestException as e:
                print(f"\nError in reservation\n")
                print(e)


    # Reset the password if it were not originally written in config.json
    if pass_not_setted:
        personal_data["password"] = ""

    # Append another "vanilla" booking_dict to the bookings dictionary in config.json
    if bookings[-1]["classroom"] != "":
        bookings.append(booking_dict)

    with open(json_file_name, "w+") as jfile:
        json.dump(config_data, jfile, indent=4)


    input("\n\nPress Enter to exit\n\n")
    close()







