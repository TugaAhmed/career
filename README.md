# Career API

A RESTful API for companies to manage job postings and applicants to browse and apply for jobs.

---

## Setup & Run Locally

--> Clone the repository:
```bash
git clone https://github.com/TugaAhmed/career.git
```

--> Install dependencies:
```bash
pip install -r requirements.txt
```


--> Create a virtual environment :
```bash

pip install virtualenv

virtualenv envname

```

--> Activate the virtual environment :
```bash
envname\scripts\activate

```

--> Install the requirements :
```bash
pip install -r requirements.txt

```

#

### Running the App

```bash
python manage.py runserver

```

### the development server will be started at http://127.0.0.1:8000/

#



## Signup example :
```bash
Invoke-WebRequest 
  -Uri "http://127.0.0.1:8000/api/auth/signup/" 
  -Method POST 
  -ContentType "application/json" 
  -Body '{"full_name": "Noha Ahmed", "email": "example@gmail.com
", "password": "StrongPass@123", "role": "company"}'
```

Response :
```bash
StatusCode        : 201
StatusDescription : Created
Content           : {"id":"7966033f-08f7-4adc-9bb8-c721b6ab87a2","email":"john@example.com","role":"applicant"}
RawContent        : HTTP/1.1 201 Created
                    Vary: Accept
                    Allow: POST, OPTIONS
                    X-Frame-Options: DENY
                    X-Content-Type-Options: nosniff
                    Referrer-Policy: same-origin
                    Cross-Origin-Opener-Policy: same-origin
                    Content-Length:...
Forms             : {}
Headers           : {[Vary, Accept], [Allow, POST, OPTIONS],
                    [X-Frame-Options, DENY], [X-Content-Type-Options,
                    nosniff]...}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : mshtml.HTMLDocumentClass
RawContentLength  : 91
```

Token : Check email or you'll find the token printed in the terminal window where your Django server is running

Click the link to verify your email: http://example.com/api/verify-email?token=john@example.com:1ulCUl:w5aCD.........



## Login example :
``` bash
$response = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/login/ -Method POST -Body '{"email":"john@example.com","password":"strongpass@123"}' -ContentType "application/json"
```

Response : 
``` bash
success message          object
------- -------          ------
   True Login successful @{refresh=eyJhbGciOiJIUzI1N............

\
```

##  Add job example : 
After signup as company and login , get token from response and create a job  

```bash
$token = $response.object.access

Invoke-RestMethod -Uri http://127.0.0.1:8000/api/jobs/create/ -Method POST -Body $jobData -ContentType "application/json" -Headers @{Authorization = "Bearer $token"}

```
Response : 

```bash
success message                  object
------- -------                  ------
   True Job created successfully @{id=a72dc120-0584-4f73-9b7702............
```