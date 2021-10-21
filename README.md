# AutoProdigit
A fast script to ease classrooms reservation on Prodigit


You have two ways to execute this program:

- Run the `PROdigit.exe`  file ( Windows only, also beware the antivirus!)
- Run the python script `PROdigit.py` 

In both cases, the file ` conifg.json` must be at the same level of the running code.


## Setup - Python case

First of all, you have to download [python3](https://www.python.org/downloads/). 
- If your are on Debian you could also use the following commands in your bash:


       sudo apt update 
       sudo apt install python3
       
After the installation, you can also install all the needed libraries. For this purpose, use the following command on your bash/command prompt:


      pip3 install -r requirements.txt


Then, to execute the python script you have to use this command into your bash/command prompt:

       
       python PROdigit.py
       
or, if you have also `python2` on your OS:

       python3 PROdigit.py
       
       
 ## Usage - English
 
 The only thing one have to understand is how the `config.json` file works and how to set it the first time.
 
1. Open it with whichever text editor you have.

2. Set your `personal_data`:<br /><br />
       If you don't want to be asked every time about your `matricola`, you can set it there!
       As for the  `password` field, **PLEASE DO NOT SET IT IF NOT NECESSARY**.
       The  `password` will be asked by the program at each execution so there is no problem for the login. 
       The only possible purpose of setting the `password` field into `config.json` is to automatically run (like with a Task Scheduler or something) the program.
       Anyway, leaving the `password` as **plaintext** into your computer is not a safe choice.
       
 3. Set your timetables:<br />
       
       As for the timetables, you have to set the `booking_list` field.
       Each of its subfields, like this one <br />   

       {
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
        <br /> <br />
        represents a reservation for a classroom. 
        For each of this reservations, the mandatory fields are the **exact** `classroom` name present on Prodigit 
        (there is some strange stuff like "AULA A3" -> **"AULA A 4"** -> "AULA A6", so beware the spaces and stuff like that),
        the `building` code (like RM031, CU001, ... ) and obviusly the time ranges of interest in the `hours` section.
        <br /><br />
         As for multiple reservation on the same day for the same class, you need to set multiple reservations (like with original Prodigit) into the `config.json` file, 
        this could change in future updates of this repository.
        <br /><br />
         

        
 ## Usage - Italian
 
 **TODO** è.è
 
 
       
