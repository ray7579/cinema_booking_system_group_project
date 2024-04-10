# Cinema Booking Website Group Project

## Description

The Cinema Booking Website is a web application developed using Python and Django framework. It facilitates the booking process for a cinema, allowing users to browse available movies, view showtimes, book tickets, make payments securely using Stripe API, generate QR codes for tickets, and receive automatic email notifications. Additionally, it supports multiple user types including Account Managers, Cinema Managers, Students, Club Representatives, and regular Customers.

## Features

- Browse available movies
- View showtimes for each movie
- Book tickets for selected shows
- Secure payments with Stripe API integration
- Generate QR codes for booked tickets
- Automatic email notifications for successful bookings and cancellations
- Multiple user types: Account Managers, Cinema Managers, Students, Club Representatives, and Customers
- Different user types have different permissions and actions:
    - **Account Managers:** Can manage user accounts, including creating, updating, and deleting accounts. Can view booking history.
    - **Cinema Managers:** Can manage movies, screens, and showtimes. Can add, update, and delete movies, screens, and showtimes.
    - **Students:** Can book tickets with student discounts.
    - **Club Representatives:** Can book tickets with group booking discounts.
    - **Customers:** Can browse movies, view showtimes, book tickets, and make payments.
      - Users will be redirected to appropriate pages based on their permissions.
      - Upon successful booking, a QR code will be generated for the ticket.
      - Users will receive an automatic email confirmation with the booking details.

## Technologies Used

- **Programming Language:** Python
- **Framework:** Django
- **Database:** PostgreSQL



