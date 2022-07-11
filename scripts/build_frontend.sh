
# remove all compiled python
find . -name "*.pyc" -delete

docker build --no-cache -t frontend_base_image:latest -f dockerfiles_aux/dockerfile.frontend .
