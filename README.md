# PropheText
This is my capstone project for the Data Science Immersive program at Galvanize.  Please contact me if you would like to see code samples for this project.

# Project Summary
For this project, I developed a comprehensive web scraping framework to aggregate information from multiple online sources about colleges and their required textbooks. This information was then fed into a custom-made algorithm to estimate the relative number of copies of each textbook that will be purchased in the upcoming college semester.

# Objective
At its core, PropheText is a model for forecasting demand for college textbooks.  Every semester, thousands of colleges require their students to purchase textbook materials for their courses.  The objective of PropheText is to predict the relative number of each textbook that will be purchased by the national student body.  While the majority of books are purchased through the school store, The National Association of College Stores found that more than 25% of purchases for this multi-billion dollar industry come from other sources online.  This information can be utilized by online used textbook sellers to intelligently prepare their inventory for the wave of purchases at the beginning of the next semester.

http://www.nacs.org/research/studentwatchfindings.aspx
https://www.nacs.org/research/industrystatistics/higheredfactsfigures.aspx

# Technologies Used
- Python packages
  - requests
  - selenium
  - lxml
  - re
  - pymongo
  - pandas
  - bokeh
  - folium
- MongoDB
  - Aggregation Framework
- AWS EC2

# Data
The data for this project was obtained by scraping the websites of over 300 college bookstores.  
![Locations of bookstores currently catalogued](/images/catalogued_stores.png?raw=true "Catalogued Bookstore Locations")
*Catalogued Bookstore Locations*

Scraped data came in a nested format and was combined with additional data sourced from the Integreated Postsecondary Education Data System, provided by the National Center for Education Statistics.  
![Course structure example](/images/course_structure.png?raw=true "Course Structure Example")
*Course Structure Example*

Data was stored in a MongoDB server running on an AWS EC2 instance.

# Model
A model was created to help textbook sellers determine which books they should stock for the upcoming semester.
![Top 1000 demanded textbooks for Fall 2016](/images/demand_scatterplot.png)
*Top 1000 demanded textbooks for Fall 2016*

Using this model, a merchant could determine which books are expensive enough to make each sale worthwhile and also in demand enough that they can safely stock up well in advance. Since this data can be collected over a month in advance of the start of a semester, merchants will have plenty of time to purchase books while demand is low.

# Future Steps
- Add over 1000 more schools
- Partner with textbook sellers to validate model with actual sales data
  - Update model using sales data to improve accuracy









