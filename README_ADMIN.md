# Trackman Analytics - Admin Features & Database Setup

## 🎯 Overview

This document covers the new admin features and persistent database setup for the Trackman Analytics platform.

## 👑 Admin Features

### Admin Panel Access
- **URL**: `/admin` (only accessible to admin users)
- **Features**:
  - User management (create, edit, delete users)
  - User statistics dashboard
  - Role-based access control
  - System overview

### User Roles
1. **Admin** (`admin`): Full access to all features including admin panel
2. **Coach** (`coach`): Access to analytics and reports
3. **User** (`user`): Basic access to upload and view reports

### Admin Panel Features
- **User Statistics**: View total users, admins, coaches, and regular users
- **User Management**: 
  - Create new users with roles
  - Edit existing user details
  - Delete users (cannot delete own account)
  - Change passwords
- **Real-time Updates**: Statistics and user list update automatically

## 🗄️ Persistent Database Setup

### Why Persistent Database?
- Users no longer need to be recreated after deployments
- Data persists across server restarts
- Better for production environments

### Database Configuration
- **File**: `trackman_analytics.db` (SQLite)
- **Location**: Project root directory
- **Backup**: Database file should be backed up regularly

### Initial Setup

1. **Run Database Initialization**:
   ```bash
   cd TrackmanAnalyticsProgram
   python init_database.py
   ```

2. **Default Users Created**:
   - **Admin**: `admin` / `admin123`
   - **Coach**: `coach` / `coach123`
   - **User**: `user` / `user123`

3. **Security Note**: Change default passwords after first login!

### Database Backup
```bash
# Backup database
cp trackman_analytics.db trackman_analytics_backup_$(date +%Y%m%d).db

# Restore database
cp trackman_analytics_backup_YYYYMMDD.db trackman_analytics.db
```

## 🚀 Deployment with Persistent Database

### Local Development
1. Run `python init_database.py` once
2. Start the application normally
3. Database persists between restarts

### Production Deployment
1. **First Deployment**:
   ```bash
   # Initialize database
   python init_database.py
   
   # Deploy backend
   eb deploy moundvision-backend-prod-lb
   ```

2. **Subsequent Deployments**:
   ```bash
   # Database persists, just deploy
   eb deploy moundvision-backend-prod-lb
   ```

### Environment Variables
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `SECRET_KEY`: JWT secret key for authentication

## 🔧 Admin API Endpoints

### User Management
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create new user
- `PUT /api/admin/users/{user_id}` - Update user
- `DELETE /api/admin/users/{user_id}` - Delete user

### Statistics
- `GET /api/admin/stats` - Get user statistics

### Authentication
All admin endpoints require admin role authentication.

## 🛡️ Security Features

### Role-Based Access Control
- Admin routes protected by `require_admin` decorator
- Frontend routes protected by `AdminRoute` component
- Users cannot access admin features without proper role

### User Protection
- Admins cannot delete their own account
- Password changes require confirmation
- Username uniqueness enforced

### Data Validation
- Role validation (admin, coach, user only)
- Username uniqueness checks
- Password hashing with bcrypt

## 📱 Frontend Integration

### Admin Panel Access
- Only visible to admin users on dashboard
- Special styling with crown icon
- Redirects non-admin users to dashboard

### User Interface
- Modal forms for user creation/editing
- Confirmation dialogs for deletions
- Real-time statistics display
- Responsive design for mobile

## 🔄 Database Migration

### Adding New Users
1. Access admin panel at `/admin`
2. Click "Add New User"
3. Fill in username, password, and role
4. Submit form

### Updating Users
1. Click "Edit" on user row
2. Modify username, password, or role
3. Submit changes

### Deleting Users
1. Click "Delete" on user row
2. Confirm deletion
3. User removed from system

## 🚨 Troubleshooting

### Database Issues
- **Database not found**: Run `python init_database.py`
- **Permission errors**: Check file permissions on database file
- **Corruption**: Restore from backup

### Admin Access Issues
- **Cannot access admin panel**: Verify user has admin role
- **Authentication errors**: Check JWT token and role
- **User not found**: Verify user exists in database

### Deployment Issues
- **Users lost after deployment**: Database not persistent, check configuration
- **Admin panel not showing**: Verify user role is 'admin'

## 📞 Support

For issues with admin features or database setup:
1. Check this documentation
2. Verify database file exists and is readable
3. Check user roles and permissions
4. Review application logs for errors

## 🔮 Future Enhancements

Potential admin features to add:
- User activity logs
- System health monitoring
- Data export/import tools
- Advanced user permissions
- Audit trails
- Bulk user operations 