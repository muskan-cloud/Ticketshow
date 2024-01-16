#TICKETSHOW_v2

In this web application , there are two types of users :

> Admin :
    > can add theaters
    > can shows to those theaters , Can perform CRUD operations on both of them!
    > can predict the bookings for the show using older trends!
    > can export Complete Report as Pdf or HTML
    > can export each theater's detail as csv
    > recieves mail of monthly report for all their theaters

> General_User :
    > can book shows
    > can rate or unrate the shows
    > recieves reminder in gspace everyday at a fixed time if they haven't booked any show in last one day!
    > can export Complete Entertainment Report as Pdf or HTML
    > recieves mail of Monthly Entertainment Report 

> Both types of users can install the ticketshow app in their system [ADD TO DESKTOP FEATURE]
> Admin User has an option of general signup!


To Run the App:

We need to open 6 terminals :

> In all the terminal start WSL! (for Windows)
> Go to the folder VUECLITICKETSHOW
> 1st Terminal : 
    > go to ticketshow [use cd command] (here we are running vue cli 'frontend')
    > run the command 'npm run serve'

> 2nd Terminal :
    > go to backend [use cd command]
    > (here we are running backend i.e flask) 
    > create a virtual environment , activate it and install requirements.txt
        > python3 -m virtualenv virenv
        > source virenv/bin/activate
        > pip install -r requirements.txt
    >after successful installation
        >run the app using python app.py

> 3rd Terminal :
    > go to backend [use cd command]
    > activate the virtual environment 
        > source virenv/bin/activate
        > run the redis server using command redis-server

> 4th Terminal :
    > go to backend [use cd command]
    > activate the virtual environment 
        > source virenv/bin/activate
    > run the celery worker by using following command:
        > celery -A app.celery worker -l info

> 5th Terminal :
    > go to backend [use cd command]
    > activate the virtual environment 
        > source virenv/bin/activate
    > run the celery-beat by using following command:
        > celery -A app.celery beat --max-interval 2 -l info

> 6th Terminal :
    > go to backend [use cd command]
    > start the mailhog server by using following command:
        > MailHog

With these setup all the features are ready to use and the app will Run!