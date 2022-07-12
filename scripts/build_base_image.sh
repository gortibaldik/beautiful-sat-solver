
# remove all compiled python
find . -name "*.pyc" -delete

docker build --no-cache -t base_image:latest -f dockerfiles/dockerfile.base_image .
