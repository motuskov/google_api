# Create the environment for the React project
FROM node
WORKDIR /google_api_frontend
COPY package*.json .
RUN npm install
COPY . .
CMD ["npm", "start"]
EXPOSE 3000
