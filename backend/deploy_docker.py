import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.97.116.207', username='ubuntu', password='UHprYHHpOM1!', timeout=15)

def run(cmd, timeout=120):
    print(f'>>> {cmd[:100]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    stdin.write('UHprYHHpOM1!\n')
    stdin.flush()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip(): print(out[:500])
    if err.strip() and 'warning' not in err.lower(): print('ERR:', err[:300])
    return out

# Wait for curl to finish
for i in range(30):
    out = run('pgrep -a curl || echo DONE')
    if 'DONE' in out:
        print('curl finished!')
        break
    print(f'  Still downloading... check {i+1}/30')
    time.sleep(10)

# Check file
run('ls -lh /tmp/docker.tgz 2>/dev/null || echo NO_FILE')

# Extract and install
run('sudo tar xzf /tmp/docker.tgz -C /tmp', timeout=60)
run('sudo cp /tmp/docker/* /usr/local/bin/')
run('sudo rm -rf /tmp/docker /tmp/docker.tgz')

# Install docker-compose plugin
run('sudo mkdir -p /usr/local/lib/docker/cli-plugins')
run('sudo curl -SL https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose', timeout=300)
run('sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose')

# Create systemd service
run('''sudo tee /etc/systemd/system/docker.service > /dev/null << 'EOF'
[Unit]
Description=Docker Application Container Engine
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/local/bin/dockerd
Restart=always
StartLimitBurst=3
StartLimitInterval=60s

[Install]
WantedBy=multi-user.target
EOF
''')

run('sudo systemctl daemon-reload')
run('sudo systemctl enable docker')
run('sudo systemctl start docker')
time.sleep(5)
run('docker --version')
run('docker compose version')
run('sudo usermod -aG docker ubuntu')

print('DONE!')
ssh.close()
