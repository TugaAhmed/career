# Career API

A RESTful API for companies to manage job postings and applicants to browse and apply for jobs.

---

## Technology Stack

- **Django & Django REST Framework**: Rapid API development with built-in admin, authentication, and serialization.
- **Django Filter**: For advanced filtering capabilities.
- **Simple JWT**: Secure JSON Web Tokens for authentication.
- **Cloudinary**: Cloud-based file storage and CDN for resumes.
- **PostgreSQL** (recommended): Robust and scalable database (you can use SQLite for local testing).
- **Python-dotenv**: Manage environment variables.

---

## Setup & Run Locally

1. Clone the repository:

git clone https://github.com/TugaAhmed/career.git

2. Install dependencies:
pip install -r requirements.txt




1. Signup example :
Write in terminal 
Invoke-WebRequest 
  -Uri "http://127.0.0.1:8000/api/auth/signup/" 
  -Method POST 
  -ContentType "application/json" 
  -Body '{"full_name": "Noha Ahmed", "email": "nohanoha295@gmail.com
", "password": "StrongPass@123", "role": "company"}'


Response :
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


Token : Check email or you'll find the token printed in the terminal window where your Django server is running

Click the link to verify your email: http://example.com/api/verify-email?token=john@example.com:1ulCUl:w5aCD.........



2. Login example :
$response = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/login/ -Method POST -Body '{"email":"john@example.com","password":"strongpass@123"}' -ContentType "application/json"


Response : 

success message          object
------- -------          ------
   True Login successful @{refresh=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey...

\


3. Add job example : 
After signup as company and login , get token from response and create a job  

$token = $response.object.access

Invoke-RestMethod -Uri http://127.0.0.1:8000/api/jobs/create/ -Method POST -Body $jobData -ContentType "application/json" -Headers @{Authorization = "Bearer $token"}