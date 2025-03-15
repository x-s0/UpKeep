@echo off
echo Checking disk for errors on C: drive...
chkdsk C: /f
echo Disk check complete. If prompted, reboot to apply fixes.