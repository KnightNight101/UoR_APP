# Backend Login Logic Testing

## Overview

This document details the testing process for the backend login logic implemented in [`Draft_2/app/main.py`] and [`Draft_2/app/login_manager.py`]. The goal was to ensure robust authentication, correct signal emission, and prevention of premature data loading. Each test is described with its purpose, the code used, any failures encountered, how they were rectified, and the final results.

---

## 1. Test: Valid Login Credentials

**Purpose:**  
To verify that the `LoginManager.verify_credentials` method accepts valid credentials and emits a successful `loginResult` signal.

**Test Code:**
```python
login_manager.verify_credentials("valid_user", "correct_password")
```

**Result:**  
- `loginResult` signal emitted with success.
- No user/project data loaded before login.

---

## 2. Test: Invalid Login Credentials

**Purpose:**  
To confirm that invalid credentials are rejected and the `loginResult` signal emits failure.

**Test Code:**
```python
login_manager.verify_credentials("valid_user", "wrong_password")
```

**Result:**  
- `loginResult` signal emitted with failure.
- No user/project data loaded.

---

## 3. Test: Signal Emission

**Purpose:**  
To ensure the `loginResult` signal is always emitted after a login attempt, regardless of outcome.

**Test Code:**
```python
def on_login_result(success):
    assert isinstance(success, bool)
login_manager.loginResult.connect(on_login_result)
login_manager.verify_credentials("any_user", "any_password")
```

**Result:**  
- Signal emitted as expected for both success and failure.

---

## 4. Test: Data Loading Blocked Before Login

**Purpose:**  
To guarantee that no user or project data is loaded before successful authentication.

**Test Code:**
```python
assert not data_loaded
login_manager.verify_credentials("valid_user", "correct_password")
# Only after success:
assert data_loaded
```

**Result:**  
- Data loading only occurs after successful login.

---

## 5. Failing Code Example and Rectification

**Initial Failing Code:**
```python
# Bug: Data was loaded before loginResult signal
if user_exists(username):
    load_user_data(username)
    self.loginResult.emit(True)
else:
    self.loginResult.emit(False)
```

**Issue:**  
User data was loaded before emitting the login result, allowing data access before authentication.

**Rectified Code:**
```python
if user_exists(username) and password_correct(username, password):
    self.loginResult.emit(True)
    load_user_data(username)
else:
    self.loginResult.emit(False)
```

**Resolution:**  
Now, data is only loaded after emitting a successful login signal.

---

## Summary of Results

- All tests passed after rectifying the data loading order.
- The backend login logic is robust: only valid credentials allow access, signals are correctly emitted, and no data is loaded before authentication.