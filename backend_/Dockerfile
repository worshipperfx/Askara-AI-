# 1. Use an official Python base image
FROM python:3.10

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy all files (including requirements.txt) into the container
COPY . .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Add this debug line
RUN pip list

# 5. Run the FastAPI app with uvicorn
EXPOSE 8080
CMD ["uvicorn", "fast_api:app", "--host", "0.0.0.0", "--port", "8080"]

# 6. Copy files
COPY topic_only.csv /app/

COPY merged_with_topics.csv /app/
