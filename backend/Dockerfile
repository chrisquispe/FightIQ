# Start from an official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (this is a caching trick —
# Docker only re-installs packages if requirements.txt changes,
# not every time you change your code)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your backend code
COPY . .

# Tell Docker this container listens on port 8000
EXPOSE 8000

# The command that starts your API when the container runs
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]