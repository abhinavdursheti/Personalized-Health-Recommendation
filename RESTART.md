# How to Restart Django Server

## Quick Restart Steps:

1. **Close the Django Server Window**
   - Look for a window titled "Django Server" 
   - Close it or press `Ctrl+C` in that window

2. **Run start.bat Again**
   - Double-click `start.bat` in the project folder
   - OR run: `.\start.bat` in PowerShell/Command Prompt

## Alternative Method (Manual):

1. Open Command Prompt or PowerShell
2. Navigate to project folder:
   ```bash
   cd "c:\Users\abhin\Downloads\health cur"
   ```
3. Activate virtual environment:
   ```bash
   venv\Scripts\activate
   ```
4. Stop any running server (press Ctrl+C)
5. Start server:
   ```bash
   python manage.py runserver 0.0.0.0:8080
   ```

## Troubleshooting:

- **Port already in use?** 
  - Close all Django server windows
  - Or use a different port: `python manage.py runserver 0.0.0.0:8081`

- **Changes not showing?**
  - Make sure you restarted the server
  - Clear browser cache (Ctrl+Shift+Delete)
