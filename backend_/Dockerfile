# this official Python base image
FROM python:3.10

#  lets set the working directory inside the container
WORKDIR /app

#  we copy all filesinto the container
COPY . .

# we install required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# then we add this debug line to make sure all dependencies are installed
RUN pip list

# run the FastAPI app with uvicorn
EXPOSE 8080
CMD ["uvicorn", "fast_api:app", "--host", "0.0.0.0", "--port", "8080"]

#copy all files
COPY topic_only.csv /app/

COPY merged_with_topics.csv /app/
