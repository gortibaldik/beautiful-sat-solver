
# remove all compiled python
find . -name "*.pyc" -delete

docker build --no-cache -t satsolver_base:latest -f dockerfiles/dockerfile.base_image .
