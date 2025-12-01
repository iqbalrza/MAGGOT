# Windows PowerShell Commands - PostgreSQL Setup

Panduan command line untuk PostgreSQL di Windows menggunakan PowerShell.

## 📍 Path Default PostgreSQL

```powershell
# PostgreSQL 15 default installation path
$PG_HOME = "C:\Program Files\PostgreSQL\15"
$PG_BIN = "$PG_HOME\bin"
$PG_DATA = "$PG_HOME\data"

# Add to PATH (optional, untuk session saat ini)
$env:Path += ";$PG_BIN"
```

## 🔧 Service Management

### Start/Stop/Restart PostgreSQL Service

```powershell
# Check service status
sc query postgresql-x64-15

# Start service
net start postgresql-x64-15

# Stop service
net stop postgresql-x64-15

# Restart service
net stop postgresql-x64-15; net start postgresql-x64-15

# Via PowerShell cmdlets (run as Administrator)
Get-Service postgresql-x64-15
Start-Service postgresql-x64-15
Stop-Service postgresql-x64-15
Restart-Service postgresql-x64-15
```

### Set Auto-start

```powershell
# Set service to start automatically
sc config postgresql-x64-15 start=auto

# Set service to manual start
sc config postgresql-x64-15 start=demand
```

## 🗄️ Database Operations

### Connect to PostgreSQL

```powershell
# Using full path
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres

# Connect to specific database
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot

# Connect with host and port
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -h localhost -p 5432
```

### Run SQL File

```powershell
# Execute SQL file
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -f quick_setup.sql

# Execute on specific database
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -f database_schema.sql

# Execute with output logging
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -f quick_setup.sql > setup_log.txt 2>&1
```

### Run Single Query

```powershell
# Execute single query
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -c "SELECT COUNT(*) FROM documents;"

# Get table list
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -c "\dt"

# Get database list
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "\l"
```

## 💾 Backup & Restore

### Backup Database

```powershell
# Full backup (custom format - recommended)
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -d maggot_chatbot -F c -f "backup.dump"

# Full backup (SQL format)
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -d maggot_chatbot -f "backup.sql"

# Backup with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -d maggot_chatbot -F c -f "backup_$timestamp.dump"

# Backup specific table
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -d maggot_chatbot -t documents -f "documents_backup.sql"

# Backup only schema (no data)
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -d maggot_chatbot --schema-only -f "schema_only.sql"

# Backup only data (no schema)
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -d maggot_chatbot --data-only -f "data_only.sql"

# Compressed backup
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -d maggot_chatbot -F c -Z 9 -f "backup_compressed.dump"
```

### Restore Database

```powershell
# Restore from custom format
& "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" -U postgres -d maggot_chatbot -c -v "backup.dump"

# Restore from SQL file
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -f "backup.sql"

# Create new database and restore
& "C:\Program Files\PostgreSQL\15\bin\createdb.exe" -U postgres maggot_chatbot_restore
& "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" -U postgres -d maggot_chatbot_restore -v "backup.dump"
```

## 🔍 Monitoring & Diagnostics

### Check Port Usage

```powershell
# Check if PostgreSQL port is open
netstat -ano | findstr :5432

# Find process using port
Get-Process -Id (Get-NetTCPConnection -LocalPort 5432).OwningProcess
```

### Check Logs

```powershell
# View recent log entries
Get-Content "C:\Program Files\PostgreSQL\15\data\log\*.log" -Tail 50

# Monitor logs in real-time
Get-Content "C:\Program Files\PostgreSQL\15\data\log\postgresql-*.log" -Wait -Tail 50

# Search for errors in logs
Get-Content "C:\Program Files\PostgreSQL\15\data\log\*.log" | Select-String "ERROR"
```

### Database Size

```powershell
# Get database size
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -c "SELECT pg_size_pretty(pg_database_size('maggot_chatbot'));"

# Get table sizes
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

## 🛠️ Maintenance

### Vacuum & Analyze

```powershell
# Vacuum database
& "C:\Program Files\PostgreSQL\15\bin\vacuumdb.exe" -U postgres -d maggot_chatbot -v

# Vacuum with analyze
& "C:\Program Files\PostgreSQL\15\bin\vacuumdb.exe" -U postgres -d maggot_chatbot -z -v

# Full vacuum (requires more time and locks)
& "C:\Program Files\PostgreSQL\15\bin\vacuumdb.exe" -U postgres -d maggot_chatbot -f -v

# Vacuum all databases
& "C:\Program Files\PostgreSQL\15\bin\vacuumdb.exe" -U postgres -a -z -v
```

### Reindex

```powershell
# Reindex database
& "C:\Program Files\PostgreSQL\15\bin\reindexdb.exe" -U postgres -d maggot_chatbot

# Reindex specific table
& "C:\Program Files\PostgreSQL\15\bin\reindexdb.exe" -U postgres -d maggot_chatbot -t chunks
```

## 🔐 User Management

### Create User

```powershell
# Create user
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE USER maggot_user WITH PASSWORD 'your_password';"

# Grant privileges
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -c "GRANT ALL PRIVILEGES ON DATABASE maggot_chatbot TO maggot_user;"
```

### Change Password

```powershell
# Change password for postgres user
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "ALTER USER postgres WITH PASSWORD 'new_password';"
```

## 📦 Database Management

### Create Database

```powershell
# Create database
& "C:\Program Files\PostgreSQL\15\bin\createdb.exe" -U postgres maggot_chatbot

# Create with options
& "C:\Program Files\PostgreSQL\15\bin\createdb.exe" -U postgres -E UTF8 -O postgres maggot_chatbot
```

### Drop Database

```powershell
# Drop database (WARNING: deletes all data!)
& "C:\Program Files\PostgreSQL\15\bin\dropdb.exe" -U postgres maggot_chatbot

# Force drop (disconnect users)
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'maggot_chatbot';"
& "C:\Program Files\PostgreSQL\15\bin\dropdb.exe" -U postgres maggot_chatbot
```

### List Databases

```powershell
# List all databases
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -l

# List with sizes
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database ORDER BY pg_database_size(datname) DESC;"
```

## 🧪 Testing Setup

### Quick Database Test

```powershell
# Test connection
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -c "SELECT 1;"

# Test pgvector extension
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"

# Test tables exist
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
```

## 📋 Automated Backup Script

Save as `backup_database.ps1`:

```powershell
# PostgreSQL Backup Script
$PG_BIN = "C:\Program Files\PostgreSQL\15\bin"
$BACKUP_DIR = "C:\Backups\PostgreSQL"
$DB_NAME = "maggot_chatbot"
$DB_USER = "postgres"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_FILE = "$BACKUP_DIR\${DB_NAME}_${TIMESTAMP}.dump"

# Create backup directory if not exists
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR
}

# Perform backup
Write-Host "Starting backup of $DB_NAME..."
& "$PG_BIN\pg_dump.exe" -U $DB_USER -d $DB_NAME -F c -f $BACKUP_FILE

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup completed: $BACKUP_FILE"
    
    # Delete backups older than 30 days
    Get-ChildItem $BACKUP_DIR -Filter "*.dump" | 
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
        Remove-Item -Force
    
    Write-Host "Old backups cleaned up"
} else {
    Write-Host "Backup failed!" -ForegroundColor Red
}
```

Run it:
```powershell
.\backup_database.ps1
```

## 🔄 Schedule Backup (Task Scheduler)

```powershell
# Create scheduled task for daily backup at 2 AM
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Scripts\backup_database.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "PostgreSQL-MaggotChatbot-Backup" -Action $action -Trigger $trigger -Principal $principal -Settings $settings
```

## 🚨 Emergency Recovery

### Database Not Starting

```powershell
# Check logs
Get-Content "C:\Program Files\PostgreSQL\15\data\log\*.log" -Tail 100

# Check service status
sc query postgresql-x64-15

# Try manual start
& "C:\Program Files\PostgreSQL\15\bin\pg_ctl.exe" -D "C:\Program Files\PostgreSQL\15\data" start

# Check port conflicts
netstat -ano | findstr :5432
```

### Corrupt Database

```powershell
# Stop PostgreSQL
net stop postgresql-x64-15

# Start in single-user mode
& "C:\Program Files\PostgreSQL\15\bin\postgres.exe" --single -D "C:\Program Files\PostgreSQL\15\data" maggot_chatbot

# REINDEX all
REINDEX DATABASE maggot_chatbot;

# Restart normally
net start postgresql-x64-15
```

---

## 💡 Tips

1. **Add psql to PATH** untuk akses lebih mudah
2. **Use aliases** di PowerShell profile:
   ```powershell
   Set-Alias psql "C:\Program Files\PostgreSQL\15\bin\psql.exe"
   Set-Alias pg_dump "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe"
   ```
3. **Setup .pgpass** untuk auto-login (buat file `%APPDATA%\postgresql\pgpass.conf`)
4. **Regular backups** sebelum upgrade atau perubahan besar
5. **Monitor disk space** untuk database dan logs

---

**Platform**: Windows 10/11  
**Shell**: PowerShell 5.1+  
**PostgreSQL**: Version 15+
