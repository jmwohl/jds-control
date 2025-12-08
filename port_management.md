# Port Management Commands

Here are some useful commands for managing processes using ports 5001 and 5002:

## Quick Commands

### Find processes using the ports:
```bash
lsof -i:5001,5002
```

### Kill specific processes by PID:
```bash
kill -9 PID_NUMBER
```

### Kill all processes using ports 5001 and 5002:
```bash
lsof -ti:5001,5002 | xargs kill -9
```

### Find Python processes running web_app.py:
```bash
pgrep -f "python.*web_app.py"
```

### Kill all Python web_app.py processes:
```bash
pkill -f "python.*web_app.py"
```

## Scripts Provided

### Start web app (with cleanup):
```bash
./start_web.sh
```

### Kill web app processes:
```bash
./kill_web.sh
```

## Troubleshooting

### If port still shows as busy:
1. Wait 30 seconds - sometimes it takes time to release
2. Use `./kill_web.sh` to force kill all processes
3. Check with `lsof -i:5001,5002` to verify it's free

### If you see "Address already in use":
1. Run `./kill_web.sh`
2. Wait a few seconds
3. Try starting again with `./start_web.sh`

### Nuclear option (kill all Python processes):
```bash
sudo pkill -f python
```
**⚠️ Warning: This will kill ALL Python processes on your system!**