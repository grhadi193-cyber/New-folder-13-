$SERVER = "ubuntu@95.38.161.104"
$REMOTE_DIR = "/home/ubuntu/backend-deploy"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Backend Deploy to 95.38.161.104" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Uploading backend-deploy.zip..." -ForegroundColor Yellow
scp "backend-deploy.zip" "${SERVER}:/home/ubuntu/"

Write-Host ""
Write-Host "[2/2] Extracting and setting up..." -ForegroundColor Yellow
ssh $SERVER "mkdir -p $REMOTE_DIR && cd $REMOTE_DIR && unzip -o /home/ubuntu/backend-deploy.zip -d . > /dev/null 2>&1 && rm /home/ubuntu/backend-deploy.zip && echo 'DONE - Files extracted!' && echo '' && echo 'Now run:' && echo '  cd $REMOTE_DIR' && echo '  nano .env' && echo '  sudo apt install docker.io docker-compose-v2 -y' && echo '  sudo systemctl enable docker && sudo systemctl start docker' && echo '  docker compose build --no-cache' && echo '  docker compose up -d'"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Backend uploaded! SSH and continue:" -ForegroundColor Green
Write-Host "  ssh ubuntu@95.38.161.104" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
