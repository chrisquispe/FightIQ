# Start from an official Node.js image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package files first — same caching trick as the backend
# Docker only reinstalls npm packages if package.json changes
COPY package.json package-lock.json ./
RUN npm install

# Now copy the rest of your frontend code
COPY . .

# Tell Docker this container listens on port 3000
EXPOSE 3000

# Start the Next.js development server
CMD ["npm", "run", "dev"]