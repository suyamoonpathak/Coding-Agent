# Step 1: Build the app
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install
ARG REACT_APP_MODEL_BASE_URL
ARG REACT_APP_EXEC_BASE_URL
ENV REACT_APP_MODEL_BASE_URL=$REACT_APP_MODEL_BASE_URL
ENV REACT_APP_EXEC_BASE_URL=$REACT_APP_EXEC_BASE_URL

# Copy the rest of the application
COPY . .

# Build the React app for production
RUN npm run build

# Step 2: Serve the app
FROM nginx:alpine

# Copy the build output to Nginx's public directory
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 to serve the app
EXPOSE 80

# Start Nginx to serve the app
CMD ["nginx", "-g", "daemon off;"]
