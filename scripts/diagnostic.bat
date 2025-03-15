@echo off
echo Starting System Diagnostic Report...
echo Please wait, this may take a few moments.

:: Set output file with timestamp in reports folder
set "timestamp=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "output_file=..\reports\Diagnostic_Report_%timestamp%.txt"

:: Header
echo === UpKeep System Diagnostic Report === > "%output_file%"
echo Generated on: %date% %time% >> "%output_file%"
echo ============================== >> "%output_file%"
echo. >> "%output_file%"

:: System Information
echo Collecting system information...
echo [System Information] >> "%output_file%"
systeminfo >> "%output_file%"
echo. >> "%output_file%"

:: Network Configuration
echo Collecting network configuration...
echo [Network Configuration] >> "%output_file%"
ipconfig /all >> "%output_file%"
echo. >> "%output_file%"

:: Active Network Connections
echo Checking active connections...
echo [Active Network Connections] >> "%output_file%"
netstat -ano >> "%output_file%"
echo. >> "%output_file%"

:: Running Processes
echo Listing running processes...
echo [Running Processes] >> "%output_file%"
tasklist >> "%output_file%"
echo. >> "%output_file%"

:: Disk Status
echo Checking disk status...
echo [Disk Status] >> "%output_file%"
wmic diskdrive list brief >> "%output_file%"
echo. >> "%output_file%"

:: Finish
echo Diagnostic report complete.
echo Report saved as: %output_file%
echo Displaying summary in app...
echo === Diagnostic Summary ===
echo System Info: Collected
echo Network Config: Collected
echo Active Connections: Collected
echo Processes: Collected
echo Disk Status: Collected
echo Full report saved to: %output_file%