# cryptoFileServerProject

## Overview
The Github repo is to organize and collectively work on our File Server Cryptography Project. 

## Getting Started
To ensure that we are able to work seemlessly on this project without running into any dependency issues we will use a virtual environment that upon activating it will share all the dependencies between us. 
There is some documentation on how to get started with virtual environments and how to activate it. 
There is also docuementation on how our github workflow should work so that we don't run into any issues when merging code.

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.11
- Git

### Setup

#### 1. Clone the Repository
```sh
git clone https://github.com/abeltran09/cryptoFileServerProject.git
cd project
```

#### 2. Activate Virtual Environment

**Windows:**
```sh
venv\Scripts\activate
```

#### 3. Install Dependencies
```sh
pip install -r requirements.txt
```
Note: If you install new libraries, make sure to add them to requirements.txt with their version

## Git Workflow

### Branching Strategy
We follow a feature-branch workflow. Each developer should create a new branch for their work and submit a pull request before merging into `main`.

#### 1. Create a New Branch
```sh
git checkout -b feature-branch-name
```
You can name the branch above what you like

#### 2. Make Changes and Commit
```sh
git add .
git commit -m "Description of changes"
```

#### 3. Push to Remote
```sh
git push origin feature-branch-name
```

#### 4. Create a Pull Request (PR)
- Open GitHub and navigate to the repository.
- Click on "New Pull Request."
- Select your branch and request a review from the team.
- Once approved, merge into `main`.
- If you install new libraries, add them to requirements.txt

#### 5. Sync with Main Branch
Before starting new work, always update your local `main` branch.
```sh
git checkout main
git pull origin main
```
