@echo off
python -m watchfiles "app" "config" "static" "templates" --filter "*.py;*.html;*.js;*.css" 

