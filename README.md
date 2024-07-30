# Chequer

Chequer is a prototype for a cheque clearing system built for the Standard Chartered Hackathon.

![output-onlinepngtools](https://github.com/user-attachments/assets/707dd1bc-dea4-46d9-8b07-d758a26b9b27)

## Description

Chequer is a modern and efficient solution for automating the cheque clearing process. It provides a streamlined workflow for processing cheques, reducing manual effort and improving accuracy.

## Features

- Easy-to-use interface for submitting and processing cheques
- Real-time status updates on cheque processing
- Secure and reliable data storage
- Integration with banking systems for seamless transaction processing

## Development Environment Setup

To set up the development environment for Chequer, follow these steps:

### 1. Clone the repository:

  ```bash
  git clone https://github.com/vsaravind01/chequer.git
  ```

### 2. Install the required dependencies:

  ```bash
  pip install -r requirements.txt
  ```

### 3. Create database:

  Use the script `chequer/init_pgdb.sh` to create the database (you can modify the credentials in the script):

  ```bash
  chmod +x scripts/init_pgdb.sh
  ./scripts/init_pgdb.sh
  ```
  > [!NOTE]
  > The script requires postgres to be installed and running on the local machine. If you are using a different database, you will need to create the database manually.

### 4. Configure the environment variables:

  Update `chequer/.env` with your database credentials:

  ```bash
  DB_HOST=<your_db_host>
  DB_PORT=<your_db_port>
  DB_USERNAME=<your_db_username>
  DB_PASSWORD=<your_db_password>
  ```

  Replace `<your_db_host>`, `<your_db_port>`, `<your_db_username>`, and `<your_db_password>` with your database credentials.

  The secret key and the algorithm for JWT is also stored in the `chequer/.env` file.

### 5. Start the development server:

  Use the script `chequer/start_server.sh` to start the development server:

  ```bash
  chmod +x scripts/start_server.sh
  ./scripts/start_server.sh
  ```

  The development server will start at the host and port specified in the `chequer/.env` file.
