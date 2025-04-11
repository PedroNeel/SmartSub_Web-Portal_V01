# Teacher Absence Management System

A comprehensive system for managing teacher absences, substitute matching, and cover plan creation, optimized to handle 50+ schools simultaneously.

## Features

- Teacher and substitute management
- Absence tracking and management
- Cover plan creation and assignment
- Advanced reporting and analytics
- Multi-school support with data isolation
- Performance optimization for high-load scenarios

## Scalability Features

The system includes several optimization features designed to handle high loads from 50+ schools:

### Database Optimization

- Connection pooling with configurable pool size and overflow
- Query optimization with indexes on frequently queried fields
- Transaction management and retry mechanisms
- Database monitoring and health checks

### Performance Improvements

- Caching system for frequently accessed data
- Rate limiting to prevent abuse
- Optimized SQL queries with proper JOIN optimizations
- Database pagination for large result sets

### Reliability Enhancements

- Error handling and recovery mechanisms
- Retry logic with exponential backoff
- Performance monitoring and alerting
- Graceful degradation under high load

## Setup and Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables
4. Initialize the database: `flask db upgrade`
5. Start the application: `gunicorn --bind 0.0.0.0:5000 main:app`

## Configuration

The application can be configured using environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: Environment (development/production)
- `CACHE_TYPE`: Cache type (SimpleCache/RedisCache)
- `REDIS_URL`: URL for Redis cache (if using RedisCache)
- `SCHOOL_NETWORKS`: Comma-separated list of IP prefixes for whitelisting

## Database Management

The application includes tools for database management and optimization:

### Database Monitoring

Run the database monitor to check for potential issues:


For scheduled monitoring, use the provided script:

### Database Optimization
Optimize the database performance:
python manage.py optimize-db

### Clean up Old Data
Remove old completed absences and cover plans:
python manage.py cleanup-old-data [DAYS]

Where `DAYS` is the number of days to keep (default: 30).
## Performance Tuning
### Connection Pool Configuration
View current connection pool settings:
python manage.py configure-pool

Update connection pool settings in `config/database.py`:
```python
"pool_size": 20,         # Default connections
"max_overflow": 30,      # Additional connections when needed
"pool_recycle": 300,     # Recycle connections after 5 minutes
Caching Configuration
Configure caching in config/__init__.py:

# Memory cache for single instance
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # 5 minutes
# Redis cache for distributed setup
app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_URL"] = redis_url
Administration
The system includes an administration interface for managing users, schools, and system settings:

User Management: Create, update, and deactivate users
School Management: Add, configure, and manage schools
System Settings: Configure global settings and defaults
Performance Monitoring: View system metrics and performance data
Security
All passwords are hashed using Werkzeug's security functions
Session data is encrypted and secured
Rate limiting prevents brute force attacks
Input validation prevents common attacks
Permissions system controls access to data
License
MIT License
