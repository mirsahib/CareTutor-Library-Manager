FROM nginx:alpine

# Copy custom code to Nginx static serving directory
COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]