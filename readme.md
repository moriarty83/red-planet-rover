## Red Planet Rover Images
By C. Marshall Moriarty
Reading, MA United States

### Red Planet Rover Images is a web application built using Python, Flask, HTML & SQL Database.

### Features
- Access Images from Spirit, Curiosity & Opportunity Rovers
- View images from all Rover cameras.
- Save favorites to a personal gallery.
- Live information on the Perseverance 2020
- All info, images thanks to NASA.

### Technologies
- Python
- Flask
- HTML/CSS
- REST API
- SQL

This site features the ability to register an account and password and login. Most of the site/application works without a user being logged in. Account creation and login is handled similarly to the Finance problem where a key for the user password is generated and that key and user info stored in the ‘users’ table of the mars.db database. However, to add images to a personal gallery or to view a personal gallery, a user must be registered and logged in.

By making use of NASA’s Mars Rover Image API available at https://api.nasa.gov, users can look up all the images taken in a single Earth Day or Martian Sol by the Spirit, Opportunity, or Curiosity rovers. This is accomplished by taking inputs from the “Lookup” page for Earth Date or Sol (Martian day). A request is then submitted using the program’s ‘lookup’ method to make a request NASA’s Mars Images API which returns a dictionary of lists that contains information for every image. This is an example of the information provided by the API for a single image:

{"id":102693,"sol":1000,"camera": {"id":20,"name":"FHAZ","rover_id":5,"full_name":"Front Hazard Avoidance Camera"},"img_src":"http://mars.jpl.nasa.gov/msl-raw-images/proj/msl/redops/ods/surface/sol/01000/opgs/edr/fcam/FLB_486265257EDR_F0481570FHAZ00323M_.JPG","earth_date":"2015-05-30","rover":{"id":5,"name":"Curiosity","landing_date":"2012-08-06","launch_date":"2011-11-26","status":"active"}}

This data is stored in the current session and then displayed on the ‘display.html’ page. Images are organized by rover camera and if more than 20 images from a single camera are available, a subset of images is presented and a link to access all images from that camera provided and those images are displayed in ‘viewall.html’.
All images are accompanied by an ‘Add to Gallery’ button. If the user is not logged in, they will be prompted to do so upon clicking this button. If the user is logged in, it will add the img_src of the image as well as the rover name, camera name, sol, earth date, current date and time, and user ID to the ‘gallery’ table in mars.db.
When the ‘Gallery’ option is selected, the user, again, is prompted to login if they are not, and if they are, it displays all images they have saved to their gallery. This is done by querying the gallery table in mars.db for all rows that match the current session’s user ID. The result is then used to populate a table using the ‘img_src’ field in the table to display images. Other data fields populate the text telling the user which rover, sol, camera and earth date the image is from.

In addition to providing images and a personal gallery to users, the ‘learn’ section embeds a number of assets from NASA’s archives to let users learn more about the Red Planet. This includes videos, as well as a stream of the current weather on Mars and the current status of the Mars 2020 mission.

This completes the summary of the Red Planet Rover app and site for CS50’s final project. Thank you and enjoy exploring the Red Planet!
