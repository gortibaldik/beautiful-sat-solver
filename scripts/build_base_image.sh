
# remove all compiled python
find . -name "*.pyc" -delete

docker build --no-cache -t base_image:latest -f dockerfiles_aux/dockerfile.base_image .
