

#From  524278368497.dkr.ecr.ap-south-1.amazonaws.com/email
From 524278368497.dkr.ecr.ap-south-1.amazonaws.com/email:email
# Create app directory
WORKDIR /app
# Install app dependencies
COPY requirements.txt ./
# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --upgrade certifi
# Bundle app source
COPY . /app
EXPOSE 8080
CMD [ "uvicorn", "main:fastApp", "--reload","--limit-concurrency","100","--timeout-keep-alive","660" ,"--host", "0.0.0.0"]
