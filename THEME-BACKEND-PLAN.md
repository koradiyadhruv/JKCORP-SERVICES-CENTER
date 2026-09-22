# JKCORP Theme and Backend Plan

## Current deployment reality
The current website is static HTML/CSS/JavaScript and GitHub Pages can host only the frontend. A Python backend cannot run inside GitHub Pages.

## Recommended production architecture
- Frontend: GitHub Pages or a static host
- Backend: Flask API on Render, Railway, Fly.io, or a VPS
- Database: PostgreSQL in production; SQLite for local development
- Email: SMTP provider or transactional email service
- Security: environment variables, HTTPS, rate limiting, input validation, spam protection

## Backend API
- `GET /api/health` - service health check
- `POST /api/inquiries` - create a customer inquiry
- `GET /api/inquiries` - admin-only inquiry list (must be protected before production)

## Required next deployment settings
1. Deploy `backend/` to a Python host.
2. Set `CORS_ORIGINS` to the real frontend domain.
3. Set `DATABASE_URL` to PostgreSQL in production.
4. Add SMTP credentials if email notifications are required.
5. Change the frontend form from `mailto:` to the deployed `/api/inquiries` endpoint.
6. Add admin authentication before exposing inquiry listing.

## Theme integration
`assets/css/themes.css` contains three reusable themes. Link it after the main stylesheet and add `data-theme="ocean"`, `data-theme="midnight"`, or `data-theme="sunset"` to the `<body>` element. The existing language switcher can be extended with a theme button later, or a theme selector can persist the choice in localStorage.
