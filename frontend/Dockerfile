FROM nginx:alpine

# Copy custom code to Nginx static serving directory
COPY . /usr/share/nginx/html

# Route /api to the backend container
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3001

CMD ["nginx", "-g", "daemon off;"]