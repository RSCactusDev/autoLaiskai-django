User
# autoLaiskai-django
This is a Django web application designed for land surveyors, which automates the preparation of letters regarding the surveyed plot and generates invitations for measurements to adjacent plots.

# Project Features
- Simple register, login feature. 
- On the settings page, users can upload their company details in .docx format (rekvizitai) and create their own letter template.
- User can upload pdf file generated by Registru Centras, it is stored in temporary folder: 
```
├─ media_cdn
   ├─ temp
   │  └─ user_* (* represents specific user id)
```
- Displays extracted data from the PDF in the CRUD interface, allowing users to select landowners to whom they want to generate letters.
- Using selenium web aplication gets land plot coordinates from Geomatininkas and land plot adress from Regia.lt and maps.lt
- Utilizes Selenium for web automation to retrieve land plot coordinates from Geomatininkas and land plot addresses from Regia.lt and maps.lt.
- Displays data retrieved via Selenium in the CRUD interface, allowing users to edit this data and subsequently generate invitations for measurements to adjacent plots.
- Users can download individual invitations in docx format, or there is an option to download all letter invitations in a zipped .zip file
# Project file structure:
```
├─ autoLaiskai-django                          # Root directory of the project
│  ├─ autolaiskai                              # Django project directory
│  │  └─ autolaiskai                           # Main Django application
│  │     ├─ algorithms                         # Stored all custom algorithms used in this project.
│  │     │  ├─ ExtractPDF.py                   # Script for extracting data from the PDF generated by Registru Centras:
                                                  Gretimybiu_pazyma.pdf.
│  │     │  ├─ mergedocx.py                    # Script for merging DOCX files (used to merge Template_KV.docx with user-provided
                                                  Rekvizitai.docx)
│  │     │  ├─ scrapingData.py                 # Script for scraping data from Registru Centras Geomatininkas to obtain plot
                                                  coordinates, and from Regia.lt and maps.lt to acquire plot addresses using
                                                  these coordinates.
│  │     ├─ authentication                     # authentication application handling user authentication, contains login,
                                                  register, logout views, described user model. 
│  │     ├─ autolaiskai
│  │     ├─ core                               # Core application with primary functionality, contains all views except
                                                  those related to authentication.
│  │     ├─ manage.py
│  │     ├─ media
│  │     ├─ media_cdn                          # Directory for storing user-uploaded media, 
│  │     │  ├─ temp                            # User-specific temporary media, where each user has their own folder in
                                                 the temp directory.
│  │     │  │  └─ user_1
│  │     │  │  └─ user_2
│  │     │  ├─ Template_KV.docx
│  │     │  └─ user_1                          # Contains the generated Template_KV.docx template for each user, customized
                                                 with their own details (rekvizitais).
│  │     │  └─ user_2  
│  │     ├─ requirements.txt
│  │     ├─ static
│  │     │  ├─ bootstrap
│  │     │  └─ mdb
│  │     ├─ static_cdn                         # Collected static files for production use            
│  │     │  ├─ admin                           # Django admin static files
│  │     │  ├─ bootstrap                       # Bootstrap framework files
│  │     │  └─ mdb                             # Tested Material Design for Bootstrap. https://mdbootstrap.com/
│  │     └─ templates                          # Django templates directory
│  │        ├─ app
│  │        │  ├─ frontpage.html
│  │        │  ├─ generate_letters.html
│  │        │  ├─ generate_letters_2.html
│  │        │  ├─ settings.html
│  │        │  └─ sidebar.html
│  │        ├─ main
│  │        │  ├─ base.html
│  │        │  ├─ base_auth.html
│  │        │  ├─ footer.html
│  │        │  └─ landing.html
│  │        └─ registration
│  │           ├─ login.html
│  │           └─ register.html
```
# Showcase
*In the showcase, one of the Selenium scripts is running in non-headless mode specifically for demonstration purposes. It can be switched to headless mode by modifying line 21 in scrapingData.py to ```options.headless = True.``` Additionally, in the showcased use of "Gretimybiu_pazyma.pdf,"  has been altered sensitive information like landowners' names and residential addresses to random names and addresses to respect privacy concerns. 
https://github.com/RSCactusDev/autoLaiskai-django/assets/78035439/ca960804-3bed-4680-a620-07ea5a8d1d89

