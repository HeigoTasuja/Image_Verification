Image Verification Tool
------------------------------------------------------------------------------------------------------------------------------------
This is a full-stack application to verify ML model predictions. It has FastAPI backend (with SQLite) that serves images and records labels, and a React frontend. The entire application is containerized and managed with Docker Compose.


Core Features
------------------------------------------------------------------------------------------------------------------------------------
Review Interface
Workflow (User can "Confirm" a correct label or "Correct" an incorrect one)
Stats Dashboard
Storage (SQLite)
Dockerized
"No More Images" handling


Bonus Feature: Undo Last Submission
------------------------------------------------------------------------------------------------------------------------------------
After submitting a label, the user has a 3-second window to click "Undo".

This action sends a DELETE request to the API, which rolls back the submission in the database and restores the image to the review queue.


How to Run the Application
------------------------------------------------------------------------------------------------------------------------------------
The only prerequisite is to have Docker and Docker Compose installed on your system.
1. Clone the Repository
git clone [[https://github.com/HeigoTasuja/Image_Verification](https://github.com/HeigoTasuja/Image_Verification)]
cd [<PATH_TO_FOLDER_WHERE_CLONED/Image_Verification>]

2. Build and Run with Docker Compose
From the root of the project (where the docker-compose.yml file is located), run the following command:

docker-compose up -d
or
docker-compose up -d --build

This will:
Build the Docker images for the backend and frontend.
Start the containers in the correct order.
Create a persistent Docker volume (sqlite_data) to store the SQLite database.

3. Access the Application
Once the containers are running, open your web browser and navigate to:
http://localhost


Technical Choices & Assumptions
------------------------------------------------------------------------------------------------------------------------------------
1. Backend (FastAPI + SQLite)
FastAPI: Chosen for its high performance, async capabilities, and automatic data validation with Pydantic.
SQLAlchemy: Used as the ORM for database interaction.
SQLite: Chosen as per the requirements for simplicity.

2. Frontend (React + Vite)
React + Vite
Axios: Used for all client-side API requests to the backend.
API Proxy: The VITE_API_BASE_URL is set to an empty string (''). In production (Docker), this allows all API calls (e.g., /api/stats) to be sent as relative paths. Nginx then intercepts these requests and proxies them to the backend, avoiding any CORS issues.

3. Orchestration (Docker Compose + Nginx)
Multi-Stage Dockerfiles
Nginx:
  -serves the static application.
  -Reverse proxy.
Backend Image: From Dockerfile creates a non-root user and runs the application as that user.
Startup Handling (HEALTHCHECK)


Potential Improvements (If I had another week)
------------------------------------------------------------------------------------------------------------------------------------
Improve main.py
    I would move endpoints from main.py to routes.py and auth_routes.py. At the moment application is small and still easy to read, but with new endpoints (e.g. authentication, statistics), main.py would be too cluttered and hard to read.

Migrate to PostgreSQL & Scale Out Backend: The current SQLite database prevents horizontal scaling.
    I would first migrate the database from SQLite to a client-server database like PostgreSQL, running in its own container.
    Once on PostgreSQL, I could scale the backend service to 2-3 replicas. Nginx would automatically act as a load balancer, this would give ability to handle more reviewers.

Decouple Frontend & Deploy to CDN:
    I would move the frontend and backend into separate repositories, each with its own CI/CD pipeline.
    This would speed up load times for global users, and the Nginx container would be API Gateway for the backend. Also BE could provide new endpoints without triggering new FE build.

Implement a Dynamic Data Ingestion Pipeline:
    Currently the app loads hardcoded list of mock images. I would replace this by creating a separate, scheduled process. This process would query a real ML model, fetch new predictions, and continuously populate the images database table.

User Authentication:
    I'd add an authentication layer to require operators to log in.
    This is the first step toward tracking per-user statistics, securing the API, and creating role-based access.

Enhanced Statistics:
    Expand the /api/stats endpoint.
    This would provide more data: per-user accuracy, accuracy breakdown per label, etc.

Frontend Error Handling:
    Implement a error-handling system.
    This would clearly inform the user if an API call fails.

Work on UI:
    Use Bootstrap.
    This would give better user experience and give out of the box UI elements.

Better Workflow:
    I would remove undo option and move reviewed images to separate page sorted correct and corrected.
    This imporves workflow, user does not have to wait 3 seconds to review another image, but navigate to another page and make changes there if needed.

Add tests