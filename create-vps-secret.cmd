@echo off
REM Tạo k8s Secret emapp-env trên VPS từ Backend\.env (chạy 1 lần).
REM Secret đi thẳng từ máy bạn -> VPS của bạn (qua SSH key), không qua bên thứ ba.
REM Chạy: mở thư mục repo, gõ  create-vps-secret.cmd
type "%~dp0Backend\.env" | ssh -i "%USERPROFILE%\.ssh\emapp_vps" root@157.66.80.93 "k3s kubectl -n emapp create secret generic emapp-env --from-env-file=/dev/stdin --dry-run=client -o yaml | k3s kubectl apply -f -"
echo.
echo === Xong. Neu thay 'secret/emapp-env created' hoac 'configured' la OK ===
pause
