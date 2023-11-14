FROM node:18.16.1-bullseye
RUN apt-get update && apt-get install -y python3 python3-pip


WORKDIR /app

COPY package.json requirements.txt ./

RUN pip3 install -r requirements.txt


COPY loadModels.py ./

RUN chmod +x loadModels.py
RUN python3 loadModels.py

RUN npm install

COPY . ./

VOLUME /app/uploads

EXPOSE 3000

ENTRYPOINT [ "node" , "index" ]