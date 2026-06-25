$SERVER = "ubuntu@95.38.161.205"
$REMOTE_DIR = "/home/ubuntu/frontend-deploy"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Frontend Deploy to 95.38.161.205" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Uploading frontend-deploy.zip..." -ForegroundColor Yellow
scp "frontend-deploy.zip" "${SERVER}:/home/ubuntu/"

Write-Host ""
Write-Host "[2/2] Extracting and setting up..." -ForegroundColor Yellow
ssh $SERVER "mkdir -p $REMOTE_DIR && cd $REMOTE_DIR && unzip -o /home/ubuntu/frontend-deploy.zip -d . > /dev/null 2>&1 && rm /home/ubuntu/frontend-deploy.zip && echo 'DONE - Files extracted!' && echo '' && echo 'Now run:' && echo '  cd $REMOTE_DIR' && echo '  sudo apt install docker.io docker-compose-v2 -y' && echo '  sudo systemctl enable docker && sudo systemctl start docker' && echo '  docker compose build --no-cache' && echo '  docker compose up -d'"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Frontend uploaded! SSH and continue:" -ForegroundColor Green
Write-Host "  ssh ubuntu@95.38.161.205" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
