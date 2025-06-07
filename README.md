# Flowlyne Project Setup Guide - Windows

Welcome to Flowlyne - a platform for connecting Egyptian businesses for mutual growth. This guide will walk you through setting up the project on a Windows laptop from scratch.

## What You'll Need
- A Windows computer
- Internet connection
- About 30 minutes

## Step 1: Install Git

1. Go to [https://git-scm.com/download/windows](https://git-scm.com/download/windows)
2. Download the installer
3. Run the installer and follow these steps:
   - Choose "Git from the command line and also from 3rd-party software"
   - Use the default settings for everything else
4. Click "Install"

**Test it worked:**
- Open your preferred terminal:
  - **Command Prompt**: Search "cmd" in Start menu
  - **PowerShell**: Search "PowerShell" in Start menu  
  - **Git Bash**: Right-click on desktop → "Git Bash Here"
- Type: `git --version`
- You should see something like "git version 2.x.x"

## Step 2: Install Python

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest Python version
3. **IMPORTANT**: During installation, check the box "Add Python to PATH"
4. Click "Install Now"

**Test it worked:**
- Open your terminal (Command Prompt, PowerShell, or Git Bash)
- Type: `python --version`
- You should see something like "Python 3.x.x"

## Step 3: Get the Project

1. Open your preferred terminal (Command Prompt, PowerShell, or Git Bash)
2. Go to your Desktop (or wherever you want the project):
   
   **Command Prompt or PowerShell:**
   ```
   cd Desktop
   ```
   
   **Git Bash:**
   ```
   cd Desktop
   ```
   *(Note: All terminals use the same command for changing directories)*

3. Clone the project:
   ```
   git clone https://github.com/YOUR_USERNAME/flowlyne.git
   ```
   *(Replace YOUR_USERNAME with the actual GitHub username)*

4. Go into the project folder:
   ```
   cd flowlyne
   ```

## Step 4: Set Up Python Environment

1. Create a virtual environment:
   ```
   python -m venv flowlyne_env
   ```

2. Activate it (choose based on what you're using):

   **Command Prompt (cmd):**
   ```
   flowlyne_env\Scripts\activate
   ```

   **PowerShell:**
   ```
   flowlyne_env\Scripts\Activate.ps1
   ```

   **Git Bash:**
   ```
   source flowlyne_env/Scripts/activate
   ```

   *(You should see (flowlyne_env) at the start of your command line)*

## Step 5: Install Required Packages

```
pip install -r requirements.txt
```

This will install Django and other packages needed for the project.

## Step 6: Set Up the Database

The database file is already included in the project, but you need to set it up:

```
python manage.py migrate
```

## Step 7: Create Admin User (Optional)

If you want to access the admin panel, create an admin user:

```
python create_flowlyne_superuser.py
```

Follow the prompts to enter:
- Email address
- Company name  
- Password

## Step 8: Start the Server

```
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

## Step 9: Open the Website

Open your web browser and go to: **http://127.0.0.1:8000/**

You should see the Flowlyne homepage!

## Available Pages

- Home: http://127.0.0.1:8000/
- Services: http://127.0.0.1:8000/services/
- Plans: http://127.0.0.1:8000/plans/
- Register: http://127.0.0.1:8000/register/
- Login: http://127.0.0.1:8000/login/
- Admin Panel: http://127.0.0.1:8000/admin/ *(if you created an admin user)*

## Stopping the Server

To stop the server, press `Ctrl + C` in the Command Prompt.

## Next Time You Want to Work on the Project

1. Open your terminal (Command Prompt, PowerShell, or Git Bash)
2. Go to the project folder: `cd Desktop\flowlyne` (use `cd Desktop/flowlyne` for Git Bash)
3. Activate the environment based on what you're using:

   **Command Prompt (cmd):**
   ```
   flowlyne_env\Scripts\activate
   ```

   **PowerShell:**
   ```
   flowlyne_env\Scripts\Activate.ps1
   ```

   **Git Bash:**
   ```
   source flowlyne_env/Scripts/activate
   ```

4. Start the server: `python manage.py runserver`

## Common Problems

**"python is not recognized"**
- Reinstall Python and make sure to check "Add Python to PATH"

**"Port 8000 is already in use"**
- Try: `python manage.py runserver 8001`
- Then go to http://127.0.0.1:8001/

**Virtual environment won't activate**
- Make sure you're in the right folder (flowlyne)
- Try the full path based on your terminal:
  - **Command Prompt**: `C:\Users\YourName\Desktop\flowlyne\flowlyne_env\Scripts\activate`
  - **PowerShell**: `C:\Users\YourName\Desktop\flowlyne\flowlyne_env\Scripts\Activate.ps1`
  - **Git Bash**: `source /c/Users/YourName/Desktop/flowlyne/flowlyne_env/Scripts/activate`

**Can't access the website**
- Make sure the server is running (you should see the "Starting development server" message)
- Try http://localhost:8000/ instead

## Project Structure

```
flowlyne/
├── flowlyne_project/     # Main Django settings
├── flowlyne/             # App with all the features
├── templates/            # HTML pages
├── static/               # CSS, JavaScript, images
├── media/                # Uploaded files
├── requirements.txt      # List of packages needed
├── manage.py            # Django management script
└── create_flowlyne_superuser.py  # Script to create admin users
```

That's it! You should now have Flowlyne running on your Windows computer. 🎉