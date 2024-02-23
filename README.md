## Environment

### production
Our website environment which is meant for public. This contains the user data.     
Git branch: `main`                                                              
Settings file: `settings_prod`

### development
We test our website in this environment so that we know everything is running fine in AWS.  
Git branch: `develop`                                                                      
Settings file: `settings_dev`

### local
We develop new features for our website in this environment in our local machine.   
Git branch: `feature/...`                                                          
Settings file: `settings_local`

## Process

### To update environment in AWS (example for development)
To create initial infrastructure in AWS (this command needs to run just once):`zappa deploy dev`

To create the database for the first time(this command needs to run just once): `zappa manage dev create_db`  

To apply the migrations: `zappa manage dev migrate`

To push the static files to their s3 location: `zappa manage dev "collectstatic --noinput"`

If code is updated for develop branch: `zappa update dev`                           

To see the current status of the deployment: `zappa status dev`

To see the logs for an environment: `zappa tail dev`

To install the fixture: `zappa manage dev "loaddata filename.json"`

