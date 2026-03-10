@echo off
echo ==============================
echo Generando build con PyInstaller
echo ==============================

REM ==============================
REM Limpiar builds anteriores
REM ==============================

rmdir /s /q build
rmdir /s /q dist
del *.spec

REM ==============================
REM Obtener ruta dinamica de libclang
REM ==============================

for /f "delims=" %%i in ('python -c "import clang, os; print(os.path.join(os.path.dirname(clang.__file__), 'native', 'libclang.dll'))"') do set LIBCLANG_PATH=%%i


REM ==============================
REM BUILD UNINSTALL
REM ==============================

echo.
echo ---- BUILD UNINSTALL ----

pyinstaller --onefile ^
--name uninstall ^
--hidden-import=pymysql ^
--hidden-import=psutil ^
--hidden-import=dotenv ^
uninstall.py


REM ==============================
REM BUILD APP (SIMSW)
REM ==============================

echo.
echo ---- BUILD SIMSW ----

pyinstaller --onedir ^
--name SIMSW ^
--collect-all transformers ^
--collect-all tokenizers ^
--hidden-import=clang ^
--hidden-import=clang.cindex ^
--hidden-import=vulberta.models.tokenization_vulberta ^
--collect-submodules vulberta ^
--add-binary "%LIBCLANG_PATH%;clang/native" ^
--add-data "analysis;analysis" ^
--add-data "auth;auth" ^
--add-data "database;database" ^
--add-data "scheduler;scheduler" ^
--add-data "scripts;scripts" ^
--add-data "static;static" ^
--add-data "templates;templates" ^
--add-data "uploads;uploads" ^
--add-data "vulberta;vulberta" ^
--add-data "ZAP_2.17.0;ZAP_2.17.0" ^
--add-data "playwright_browsers;playwright_browsers" ^
run.py


REM ==============================
REM BUILD INSTALL
REM ==============================

echo.
echo ---- BUILD INSTALL ----

pyinstaller --onedir ^
--name install ^
--collect-all transformers ^
--collect-all tokenizers ^
--hidden-import=clang ^
--hidden-import=clang.cindex ^
--hidden-import=vulberta.models.tokenization_vulberta ^
--collect-submodules vulberta ^
--add-binary "%LIBCLANG_PATH%;clang/native" ^
--add-data "dist\uninstall.exe;." ^
--add-data "dbSIMSW.sql;." ^
--add-data "analysis;analysis" ^
--add-data "auth;auth" ^
--add-data "database;database" ^
--add-data "scheduler;scheduler" ^
--add-data "scripts;scripts" ^
--add-data "static;static" ^
--add-data "templates;templates" ^
--add-data "uploads;uploads" ^
--add-data "vulberta;vulberta" ^
--add-data "ZAP_2.17.0;ZAP_2.17.0" ^
--add-data "playwright_browsers;playwright_browsers" ^
install.py


REM ==============================
REM Unir carpetas
REM ==============================

echo.
echo ---- UNIENDO BUILDS ----

xcopy dist\install\* dist\SIMSW\ /E /I /Y

REM Copiar SIMSW.exe dentro de _internal para que install lo genere luego
copy dist\SIMSW\SIMSW.exe dist\SIMSW\_internal\SIMSW.exe /Y

REM limpiar carpeta install
rmdir /s /q dist\install


echo.
echo ==============================
echo BUILD FINALIZADO
echo Carpeta final: dist\SIMSW
echo ==============================

pause