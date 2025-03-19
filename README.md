# cryptoFileServerProject

## Overview
A brief description of the project goes here. Explain its purpose and key features.

## Getting Started

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.11
- Git
- Virtual Environment (venv)

### Setup

#### 1. Clone the Repository
```sh
git clone https://github.com/abeltran09/cryptoFileServerProject.git
cd project
```

#### 2. Create and Activate Virtual Environment

**Windows:**
```sh
venv\Scripts\activate
```

#### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

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

#### 5. Sync with Main Branch
Before starting new work, always update your local `main` branch.
```sh
git checkout main
git pull origin main
```
