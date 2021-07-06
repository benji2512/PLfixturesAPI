# Premier League Fixtures API  
This API will be designed to feed *up to date* fixture details to a webpage and Android/IOS app. I will keep the website and apps in different repos to keep maintainence easy  

It will be built using: 
- OpenFaaS as the provider  
- MongoDB as the database  
- Python as the main language  
  
It will be built over time and I will update the below checklist according to the progress being made and the newer additions I think up.  
- [ ] Populate MongoDB with per-team fixture information :thinking:
  -  Automating it obviously
  - [ ] Clean up returned data into a per-team basis in MongoDB styling
  - [ ] Write script to push gathered information to MongoDB
- [ ] Setup CI workflow for data comparison :partying_face:
  - [ ] Choose a provider