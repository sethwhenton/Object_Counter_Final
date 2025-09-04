# CI/CD Pipeline Setup Guide

## 🚀 **GitLab CI/CD Pipeline for Object Counting API**

This document describes the comprehensive CI/CD pipeline setup for the MySQL-migrated Object Counting API.

## 📋 **Pipeline Overview**

The CI/CD pipeline consists of three main stages:

1. **Test Stage** - Comprehensive testing with multiple test suites
2. **Build Stage** - Application validation and artifact preparation
3. **Deploy Stage** - Staging and production deployments

## 🔧 **Pipeline Configuration**

### **Main Pipeline File: `.gitlab-ci.yml`**

The pipeline is configured with the following features:

- **Multi-stage testing**: API tests, Storage tests, and Full test suite
- **MySQL service integration**: Automated database setup and testing
- **Artifact management**: Test reports and build artifacts
- **Manual deployment gates**: Controlled staging and production deployments
- **Environment-specific configurations**: Test, staging, and production environments

### **Test Jobs**

#### **1. Full Test Suite (`test`)**
- Runs comprehensive test suite (44 tests)
- Includes API, Storage, and Integration tests
- Generates JUnit XML reports
- Runs on main, develop, and merge requests

#### **2. API Tests Only (`test_api`)**
- Quick API validation (30 tests)
- Fast feedback for API changes
- Runs on main, develop, and merge requests

#### **3. Storage Tests Only (`test_storage`)**
- Database and model validation (14 tests)
- Ensures data integrity
- Runs on main, develop, and merge requests

## 🗄️ **Database Setup**

### **CI Database Configuration**

The pipeline uses MySQL 8.0 service with the following configuration:

```yaml
services:
  - mysql:8.0
variables:
  MYSQL_ROOT_PASSWORD: root
  MYSQL_DATABASE: obj_detect_test_db
  MYSQL_USER: root
  MYSQL_PASSWORD: root
  MYSQL_HOST: mysql
```

### **Environment Variables**

The following environment variables are automatically set:

```bash
OBJ_DETECT_ENV=test
OBJ_DETECT_MYSQL_DB=obj_detect_test_db
OBJ_DETECT_MYSQL_USER=root
OBJ_DETECT_MYSQL_PWD=root
OBJ_DETECT_MYSQL_HOST=mysql
```

## 🧪 **Testing Infrastructure**

### **Test Runner Commands**

The pipeline uses the comprehensive test runner:

```bash
# Full test suite
python tests/test_runner.py --test all --verbose

# API tests only
python tests/test_runner.py --test api

# Storage tests only
python tests/test_runner.py --test storage
```

### **CI-Specific Test Runner**

For enhanced CI integration, use the specialized CI test runner:

```bash
python tests/ci_test_runner.py
```

This runner provides:
- JUnit XML report generation
- Enhanced error reporting
- CI environment setup
- Test result summaries

## 📊 **Test Reports and Artifacts**

### **Generated Artifacts**

1. **JUnit XML Reports**: `backend/test-results.xml`
2. **Test Results Directory**: `backend/test-results/`
3. **Build Artifacts**: Application files and dependencies

### **Artifact Retention**

- Test reports: 1 week
- Build artifacts: 1 hour
- Automatic cleanup after expiration

## 🚀 **Deployment Stages**

### **Staging Deployment**

- **Trigger**: Manual deployment from develop branch
- **Environment**: Staging
- **Purpose**: Pre-production testing and validation

### **Production Deployment**

- **Trigger**: Manual deployment from main branch or tags
- **Environment**: Production
- **Purpose**: Live application deployment

## 🔄 **Pipeline Triggers**

### **Automatic Triggers**

- **Main branch**: Full pipeline execution
- **Develop branch**: Full pipeline execution
- **Merge requests**: Full pipeline execution

### **Manual Triggers**

- **Staging deployment**: Manual approval required
- **Production deployment**: Manual approval required

## 📈 **Pipeline Monitoring**

### **Success Criteria**

- All tests must pass (44/44 tests)
- No critical errors or failures
- Database connectivity verified
- Application imports successfully

### **Failure Handling**

- Failed tests block deployment
- Detailed error reporting in GitLab UI
- Artifact preservation for debugging
- Automatic cleanup of test data

## 🛠️ **Local Development**

### **Running CI Tests Locally**

To run the same tests as the CI pipeline:

```bash
# Set up environment
export OBJ_DETECT_ENV=test
export OBJ_DETECT_MYSQL_DB=obj_detect_test_db
export OBJ_DETECT_MYSQL_USER=root
export OBJ_DETECT_MYSQL_PWD=root
export OBJ_DETECT_MYSQL_HOST=localhost

# Run tests
cd backend
python tests/test_runner.py --test all --verbose
```

### **CI Database Setup**

For local CI testing:

```bash
cd backend
python setup_ci_database.py
```

## 📝 **Pipeline Customization**

### **Adding New Test Suites**

1. Create test file in appropriate directory
2. Update test runner to include new tests
3. Modify CI configuration if needed

### **Environment Variables**

Add new environment variables in the `.gitlab-ci.yml` file:

```yaml
variables:
  NEW_VARIABLE: value
```

### **Service Dependencies**

Add new services to the pipeline:

```yaml
services:
  - mysql:8.0
  - redis:latest
```

## 🎯 **Best Practices**

### **Commit Messages**

Use conventional commit messages:

```
feat: add new API endpoint
fix: resolve database connection issue
test: add comprehensive test coverage
docs: update CI/CD documentation
```

### **Branch Strategy**

- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: Feature development
- **hotfix/***: Critical fixes

### **Testing Strategy**

- Write tests for all new features
- Maintain test coverage above 90%
- Use descriptive test names
- Include both positive and negative test cases

## 🚨 **Troubleshooting**

### **Common Issues**

1. **MySQL Connection Timeout**
   - Check service configuration
   - Verify environment variables
   - Increase connection timeout

2. **Test Failures**
   - Review test logs
   - Check database setup
   - Verify dependencies

3. **Build Failures**
   - Check requirements.txt
   - Verify Python version
   - Review import statements

### **Debug Commands**

```bash
# Check MySQL connectivity
mysqladmin ping -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD"

# Verify environment
env | grep OBJ_DETECT

# Test database setup
python setup_ci_database.py
```

## 📚 **Additional Resources**

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [MySQL Docker Image](https://hub.docker.com/_/mysql)
- [Python Testing Best Practices](https://docs.python.org/3/library/unittest.html)

## 🎉 **Pipeline Status**

✅ **Pipeline Configuration**: Complete
✅ **Test Infrastructure**: Complete
✅ **Database Setup**: Complete
✅ **Deployment Stages**: Complete
✅ **Documentation**: Complete

**The CI/CD pipeline is ready for production use!**


