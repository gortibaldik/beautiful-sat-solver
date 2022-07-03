
# remove all compiled python
find . -name "*.pyc" -delete

# remove compiled frontend
rm -r client/node_modules

docker build --no-cache -t base_image:latest -f dockerfile.base_image .
