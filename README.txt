# forcedlaborrisk 

INTRODUCTION

This app/dashboard uses open source international trade data to detect risk of forced or child labor in the business supply chain by commodity classes, country, and year. 

This github repository (repo) builds an app or dashboard with a user interface, complete with a tutorial video for the first time user. 

Built in Python 3, the repo is self-contained, has all the data it needs to run correctly in its current form, and may be used to create and host an app on AWS or any other platform which connects with GitHub. 

The packages used are listed in requirements.txt. 

I built it as the Open Trade Data Pilot for the STREAMS Project, Verite, in Apr 2022. '

For more information on Verite or the STREAMS Project please visit their websites https://verite.org and https://verite.org/streams/, respectively.


DATA AND SOURCES

There are four data that are needed for the app to run. I acquired (2-4) from UN Comtrade using a free trial subscription. 

1. Countries, Commodity combinations known to have child or forced labor from U. S. Dept. of Labor (https://www.dol.gov/agencies/ilab/reports/child-labor/list-of-goods)

2. A list of Countries/Trade groups.

3. A list of Commodities.

4. International Trade Data for commodity groups (annual)

The current data used in this app is based on the year 2021 and 2022 and is limited to the trade of one commodity Cotton - 52, for all the countries areas listed by the UN Comtrade website (https://comtradeplus.un.org). 

This app was built for Verite and is not affiliated with UN Comtrade in any way. We thank them for the trial subscription and data. 


SAMPLE USE

One live instance as a sample of what it looks like and does, is hosted for free at the streamlit cloud. The URL is: 

https://arshsinghphd-forcedlaborrisk-github-io-app-5pqff6.streamlit.app

You may need to ask the "Get this app up" and wait for it streamlit to spin the container.


IDEAS FOR YOU CAN DO WITH IT

It is a public repository and can be in one of the following ways.

1. Use it in its current form for education of how the commodities that are made using child or forced labor disseminate across international trade.

2. Use it in its current form for learning/teaching about app development

3. Take the part if the code that makes the graph and use it in a completely different purpose to visualize other data.

4. Develop it further (Please read FOR DEVELOPERS section for notes):

   A. Add more commodities and more current data static data from UN Comtrade or 

   B. Use connect the app directly to the UN Comtrade Database (https://comtradeplus.un.org) using their API. 

	A paid subscription is required to use the API. 

	There may be discounts for some types of users based on geography or end use. 

	More information can be found on their website. 


FOR DEVELOPERS:

There is no continued support for this repo. 

If you need to discuss collaboration or learn about the project, write to:

	Allison, aarbib@verite.org.

For technical clarifications or comments, write to: 

	Arsh, arshsinghphd@gmail.com.
 
1. FILES and FOLDERS:
<<<<<<< HEAD:README.txt

	The repo has three functions (python3): 

		app.py, 

		lookup.py, and 

		countryNode.py.

	A list of packages needed to create the docker/venv

		requirements.txt

	Subdirectories:

		"data" stores data, 

		"images" stores images. 

		The program  creates two called "lib" and "__pycache__". 

=======
	
 The repo has three functions (python3): 
 	1. app.py, 
  	2. lookup.py, and 
	3.countryNode.py.

A list of packages needed to create the docker/venv
	
  	requirements.txt

Subdirectories:

	"data" stores data, 
	
 	"images" stores images. 

	The program  creates two called 
	
 	"lib" and 
	
 	"__pycache__". 
>>>>>>> a032dc85017adbb26a6971716600759eab2b85c2:README.md

2. WORKING

app.py 
<<<<<<< HEAD:README.txt

	Makes the user interface using streamlit.

	Takes inputs from user

	Creates graphs 

	Allows users to download csv or xls files.

		calls:

			lookup.py. 

		Uses: 

			(2) images to make thumbnail and logo. 

			(1) video for demo

			(6) csv files

				areas (list of trade areas)

				(M for import, X for export)

				M_52_2021 

				M_52_2022 

				X_52_2021

				X_52_2022

				list_fl_cotton
=======
	
 Makes the user interface using streamlit.

 Takes inputs from user

 Creates graphs 

 Allows users to download csv or xls files.

  calls:

   lookup.py. 

  Uses: 			

	(2) images to make thumbnail and logo.		
   	
    	(1) video for demo
     
	(6) csv files
				
    		areas (list of trade areas)
		
  		(M for import, X for export)
		
  		M_52_2021 
		
  		M_52_2022 
			
   		X_52_2021
		
  		X_52_2022
		
  		list_fl_cotton.csv
>>>>>>> a032dc85017adbb26a6971716600759eab2b85c2:README.md

lookup.py 

	analyses trade data,
<<<<<<< HEAD:README.txt

	matching countries in trade file with DoL's list of Forced and Child Labor, 

	processes these to make pyvis graphs.

		is called by: 

			app.py

		calls:

=======
 
	matching countries in trade file with DoL's list of Forced and Child Labor, 
 
	processes these to make pyvis graphs.
 
		is called by: 
  
			app.py
   
		calls:
  
>>>>>>> a032dc85017adbb26a6971716600759eab2b85c2:README.md
			countryNode.py

countryNode.py

	creates a class Node
 
	
