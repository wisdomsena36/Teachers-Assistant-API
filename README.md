# Teachers Assistant API

## Table of Contents
- [Introduction](#introduction)
- [Project Overview](#project-overview)
- [MVP (Minimum Viable Product)](#mvp-minimum-viable-product)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
  - [Endpoints](#endpoints)
    - [Status Check](#status-check)
    - [User Registration](#user-registration)
    - [Verify Email](#verify-email)
    - [Login](#login)
    - [Logout](#logout)
    - [Profile](#profile)
    - [Update Profile](#update-profile)
    - [Forgot Password](#forgot-password)
    - [Reset Password](#reset-password)
    - [Generate Letter](#generate-letter)
    - [Generate Examination Questions](#generate-examination-questions)
    - [Download Generated Letter](#download-generated-letter)
    - [Get User Letters](#get-user-letters)
    - [Get Specific User Letter](#get-specific-user-letter)
    - [Download and Save Letter](#download-and-save-letter)
    - [Delete User Letter](#delete-user-letter)
    - [Update User Letter](#update-user-letter)
    - [Admin Login](#admin-login)
    - [Get All Users (Admin)](#get-all-users-admin)
    - [Get Specific User (Admin)](#get-specific-user-admin)
    - [Get All Letters (Admin)](#get-all-letters-admin)
    - [Get User Letters (Admin)](#get-user-letters-admin)
    - [Delete Letter (Admin)](#delete-letter-admin)
- [Contributing](#contributing)
- [Technology Stack](#technology-stack)
- [Meet the Team](#meet-the-team)
- [Licensing](#licensing)

## Introduction

The Teachers Assistant API is designed to support teachers in Ghana by automating the generation of application letters and examination questions with a Marking Scheme Generator using AI. This project aims to save time and improve efficiency by exporting outputs into Word documents for ease of use.

## Project Overview

The Teachers Assistant API offers two main features:

1. **Teacher Application Letters Generator**: Generates various types of application letters for teachers.
2. **Examination Questions with Marking Scheme Generator**: Creates examination questions along with marking schemes.

Both features export their outputs into Word documents, making it convenient for teachers to use.

## MVP (Minimum Viable Product)

- User authentication (registration, login, profile management)
- Generation of various application letters
- Creation of examination questions with marking schemes
- Exporting generated content to Word documents
- Admin features for managing users and generated content

## Architecture

The Teachers Assistant API is structured with a focus on modularity and scalability. The core components include:

- **Authentication**: Manages user authentication, registration, and profile management.
- **Letter Generation**: Handles the creation of various application letters based on user inputs.
- **Examination Generation**: Generates examination questions and marking schemes.
- **Admin**: Provides administrative features for managing users and generated content.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-repository/teachers-assistant-api.git
    ```
2. Navigate to the project directory:
    ```sh
    cd teachers-assistant-api
    ```
3. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
4. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
5. Set up environment variables:
    ```sh
    cp .env.example .env
    ```
   Modify the `.env` file with your configuration.

6. Run the application:
    ```sh
    python app.py
    ```

## Usage

### Endpoints

#### Status Check
- **URL**: `/`
- **Method**: GET
- **Description**: Check the status of the API.
- **Response**: `{"message": "Welcome"}`

#### User Registration
- **URL**: `/register`
- **Method**: POST
- **Description**: Register a new user.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "first_name": "First",
    "last_name": "Last",
    "phone_number": "1234567890",
    "gender": "M"
  }
  ```
- **Response**: `{"email": "user@example.com", "message": "User created successfully. Please check your email for verification."}`

#### Verify Email
- **URL**: `/verify_email`
- **Method**: POST
- **Description**: Verify the user's email.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "verification_code": "123456"
  }
  ```
- **Response**: `{"message": "Email verified successfully. You can now log in."}`

#### Login
- **URL**: `/login`
- **Method**: POST
- **Description**: User login.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**: `{"email": "user@example.com", "message": "Logged in successfully"}`

#### Logout
- **URL**: `/logout`
- **Method**: DELETE
- **Description**: User logout.
- **Response**: Redirection to `/`

#### Profile
- **URL**: `/profile`
- **Method**: GET
- **Description**: Get the user's profile.
- **Response**: User profile details.

#### Update Profile
- **URL**: `/profile`
- **Method**: PUT
- **Description**: Update the user's profile.
- **Request Body**:
  ```json
  {
    "first_name": "NewFirst",
    "last_name": "NewLast",
    "phone_number": "0987654321",
    "gender": "F"
  }
  ```
- **Response**: `{"message": "Profile updated successfully"}`

#### Forgot Password
- **URL**: `/forgot_password`
- **Method**: POST
- **Description**: Initiate password reset process.
- **Request Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response**: `{"message": "Reset code sent to your email"}`

#### Reset Password
- **URL**: `/reset_password`
- **Method**: POST
- **Description**: Reset user's password.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "reset_code": "123456",
    "new_password": "newpassword123"
  }
  ```
- **Response**: `{"message": "Password updated successfully"}`

#### Generate Letter
- **URL**: `/generate_letter`
- **Method**: POST
- **Description**: Generate a letter.
- **Request Body**: 
  - For `maternity_leave_letter`:
    ```json
    {
      "letter_type": "maternity_leave_letter",
      "name": "Jane Doe",
      "staffid": "12345",
      "phone": "1234567890",
      "registeredno": "987654",
      "school": "Example School",
      "address": "123 Example St",
      "district_town": "Example Town",
      "address_town": "Example Town",
      "district": "Example District",
      "date_on_letter": "2023-07-11"
    }
    ```
  - For `upgrading_application_letter`:
    ```json
    {
      "letter_type": "upgrading_application_letter",
      "name": "John Doe",
      "staffid": "12345",
      "phone": "1234567890",
      "registeredno": "987654",
      "school": "Example School",
      "address": "123 Example St",
      "district_town": "Example Town",
      "address_town": "Example Town",
      "district": "Example District",
      "date_on_letter": "2023-07-11",
      "years_in_service": "5",
      "program": "Masters in Education",
      "year_completed": "2020",
      "current_rank": "Senior Teacher",
      "next_rank": "Principal Teacher"
    }
    ```
  - For `acceptance_of_appointment_letter`:
    ```json
    {
      "letter_type": "acceptance_of_appointment_letter",
      "name": "John Doe",
      "reference": "Ref123",
      "phone": "1234567890",
      "school": "Example School",
      "address": "123 Example St",
      "region_town": "Example Town",
      "address_town": "Example Town",
      "region": "Example Region",
      "date_on_letter": "2023-07-11",
      "date_on_appointment_letter": "2023-06-01"
    }
    ```
  - For `transfer_or_reposting_letter`:
    ```json
    {
      "letter_type": "transfer_or_reposting_letter",
      "name": "Jane Doe",
      "staffid": "12345",
      "phone": "1234567890",
      "registeredno": "987654

",
      "school": "Example School",
      "address": "123 Example St",
      "district_town": "Example Town",
      "address_town": "Example Town",
      "district": "Example District",
      "date_on_letter": "2023-07-11",
      "years_in_school": "3",
      "reason": "Family Relocation",
      "new_school": "New Example School"
    }
    ```
  - For `release_transfer_letter`:
    ```json
    {
      "letter_type": "release_transfer_letter",
      "name": "Jane Doe",
      "staffid": "12345",
      "phone": "1234567890",
      "registeredno": "987654",
      "school": "Example School",
      "address": "123 Example St",
      "district_town": "Example Town",
      "address_town": "Example Town",
      "district": "Example District",
      "date_on_letter": "2023-07-11",
      "years_in_school": "3",
      "reason": "New Job Opportunity",
      "new_dist_reg": "New District",
      "curr_dist_reg": "Current District",
      "level_of_transfer": "District Level"
    }
    ```
  - For `salary_reactivation_letter`:
    ```json
    {
      "letter_type": "salary_reactivation_letter",
      "name": "John Doe",
      "staffid": "12345",
      "phone": "1234567890",
      "registeredno": "987654",
      "school": "Example School",
      "address": "123 Example St",
      "district_town": "Example Town",
      "address_town": "Example Town",
      "district": "Example District",
      "date_on_letter": "2023-07-11",
      "month_or_s": "January",
      "circuit": "Example Circuit"
    }
    ```
- **Response**: `{"message": "Letter generated successfully", "download_url": "url_to_download_letter"}`

#### Generate Examination Questions
- **URL**: `/generate_examination_questions`
- **Method**: POST
- **Description**: Generate examination questions with marking schemes.
- **Request Body**: 
  ```json
  {
    "school_name": "School Name",
    "term": "Term",
    "subject": "Subject",
    "class": "Class",
    "duration": "Duration",
    "topics_taught": "Topics",
    "num_of_mul_choice_ques": 10,
    "num_of_subjective_ques": 5,
    "num_of_sub_ques_to_ans": 3
  }
  ```
- **Response**: `{"message": "Examination document created successfully", "download_url": "url_to_download_document"}`

#### Download Generated Letter
- **URL**: `/download_generated_letter/<file_id>/<template_name>`
- **Method**: GET
- **Description**: Download a generated letter.
- **Response**: Word document file

#### Get User Letters
- **URL**: `/user_letters`
- **Method**: GET
- **Description**: Retrieve all letters generated by the user.
- **Response**: List of letters generated by the user.

#### Get Specific User Letter
- **URL**: `/user_letters/<letter_id>`
- **Method**: GET
- **Description**: Retrieve a specific letter generated by the user.
- **Response**: Details of the specific letter.

#### Download and Save Letter
- **URL**: `/download_save_letter/<letter_id>`
- **Method**: GET
- **Description**: Download and save a specific letter generated by the user.
- **Response**: Word document file

#### Delete User Letter
- **URL**: `/letter/<letter_id>`
- **Method**: DELETE
- **Description**: Delete a specific letter generated by the user.
- **Response**: `{"message": "Letter deleted successfully"}`

#### Update User Letter
- **URL**: `/update_letter/<letter_id>`
- **Method**: PUT
- **Description**: Update the details of a specific letter generated by the user.
- **Request Body**: Fields to be updated (e.g., content, filename, type).
- **Response**: `{"message": "Letter updated successfully"}`

#### Admin Login
- **URL**: `/admin/login`
- **Method**: POST
- **Description**: Admin login.
- **Request Body**:
  ```json
  {
    "email": "admin@example.com",
    "password": "adminpassword"
  }
  ```
- **Response**: `{"email": "admin@example.com", "message": "Logged in successfully as Admin"}`

#### Get All Users (Admin)
- **URL**: `/admin/users`
- **Method**: GET
- **Description**: Retrieve all users (Admin only).
- **Response**: List of all users.

#### Get Specific User (Admin)
- **URL**: `/admin/user`
- **Method**: POST
- **Description**: Retrieve details of a specific user (Admin only).
- **Request Body**:
  ```json
  {
    "id": "user_id",
    "last_name": "LastName"
  }
  ```
- **Response**: Details of the specific user.

#### Get All Letters (Admin)
- **URL**: `/admin/letters`
- **Method**: GET
- **Description**: Retrieve all letters generated by users (Admin only).
- **Response**: List of all letters.

#### Get User Letters (Admin)
- **URL**: `/admin/letter`
- **Method**: POST
- **Description**: Retrieve letters generated by a specific user (Admin only).
- **Request Body**:
  ```json
  {
    "id": "user_id",
    "last_name": "LastName"
  }
  ```
- **Response**: List of letters generated by the specific user.

#### Delete Letter (Admin)
- **URL**: `/admin/letter/<letter_id>`
- **Method**: DELETE
- **Description**: Delete a specific letter generated by a user (Admin only).
- **Response**: `{"message": "Letter deleted successfully"}`

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## Technology Stack

- **Database Development**: SQLAlchemy
- **Backend Development**: Python, Flask Web Framework
- **Third-Party Services**: Gemini API, Microsoft Word API

## Meet the Team

- **Wisdom Edem Sena**: Project Lead and Developer

## Licensing

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.