# THINKedIn Testing Guide

## Prerequisites

Before testing, make sure you have:
- ✅ Supabase project set up
- ✅ `.env` file configured with API keys
- ✅ Python virtual environment created (`venv/`)
- ✅ Dependencies installed

---

## Step-by-Step Testing

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd backend
source ../venv/bin/activate
python app.py
```

**Expected Output:**
```
✓ Configuration validated successfully
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5001
 * Running on http://0.0.0.0:5001
Press CTRL+C to quit
```

**If you see errors:**
- `ModuleNotFoundError`: Run `pip install -r backend/requirements.txt`
- `Configuration error`: Check your `.env` file has all required keys
- Port already in use: Kill the process on port 5001 or change the port

---

### Step 2: Test the Health Check

In a new terminal (keep backend running):

```bash
curl http://localhost:5001/api/health
```

**Expected Response:**
```json
{"status":"healthy"}
```

✅ **If you see this, your backend is working!**

---

### Step 3: Check the Referral Code

You need a valid referral code to sign up. Let's check what it is:

**Option A: Check the database**
1. Go to your Supabase dashboard
2. Click "Table Editor" → "platform_settings"
3. Look at the `active_referral_code` field
4. Default is: `LAUNCH_2025`

**Option B: Use the special codes**
From your `.env` file:
- `OPS` - Regular member code
- `SUPER_OPS_2025` - Director code (gives admin access)

---

### Step 4: Test Signup Flow

1. **Open the signup page:**
   ```bash
   open frontend/signup.html
   ```
   (On Windows: `start frontend/signup.html`)
   (On Linux: `xdg-open frontend/signup.html`)

2. **Fill in Step 1 - Account Creation:**
   - Email: `test@purdue.edu`
   - Password: `TestPassword123!`
   - Confirm Password: `TestPassword123!`
   - Referral Code: `SUPER_OPS_2025` (to get director access)
   - Click "Next"

3. **Step 2 - Resume Upload (Optional for now):**
   - You can skip this by clicking "Skip for Now"
   - Or upload a PDF resume to test the AI parsing

4. **Step 3 - Profile Completion:**
   - Full Name: `Test User`
   - Major: `Computer Science`
   - Graduation Year: `2025`
   - Click "Complete Signup"

**Expected Result:**
- ✅ Success message: "Account created successfully!"
- ✅ Automatically redirected to `profile.html`

**Check Backend Terminal:**
You should see logs like:
```
POST /auth/signup - 201
```

**Check Supabase:**
1. Go to Supabase → Table Editor → `user_profiles`
2. You should see your new user with:
   - `full_name`: "Test User"
   - `major`: "Computer Science"
   - `graduation_year`: 2025
   - `is_director`: true (because you used SUPER_OPS_2025)

---

### Step 5: Test Login Flow

1. **Open login page:**
   ```bash
   open frontend/login.html
   ```

2. **Login with your test account:**
   - Email: `test@purdue.edu`
   - Password: `TestPassword123!`
   - Click "Sign In"

**Expected Result:**
- ✅ Success message
- ✅ Redirected to `home.html` (the alumni directory)

**Check Browser Console:**
- Press F12 (or Cmd+Option+I on Mac)
- Go to "Application" → "Local Storage" → `file://`
- You should see:
  - `think_auth_token`: (a long JWT token)
  - `think_user_data`: (JSON with your user info)

---

### Step 6: Test Profile Editor

1. **Navigate to profile page:**
   - Click on "Profile" in the navigation
   - Or directly open: `frontend/profile.html`

2. **Check that your profile loaded:**
   - ✅ Your name appears in the form
   - ✅ Your major and graduation year are filled in
   - ✅ The preview card on the right shows your info

3. **Test live preview:**
   - Type in the "Current Company" field (e.g., "Google")
   - Type in the "Current Title" field (e.g., "Software Engineer")
   - **Watch the preview card update in real-time!** ✨

4. **Test editing fields:**
   - Update your bio
   - Change your location
   - Add career interests (comma-separated): `Technology, Finance, Healthcare`
   - Watch the industry tags appear in the preview

5. **Test saving:**
   - Click "Save Changes"
   - **Expected Result:** Green success message "Profile updated successfully!"
   - Refresh the page - your changes should persist

6. **Test canceling:**
   - Make some changes (don't save)
   - Click "Cancel"
   - Your changes should revert

**Check Backend Terminal:**
You should see:
```
GET /api/profile - 200
PUT /api/profile - 200
```

**Check Supabase:**
1. Go to Table Editor → `user_profiles`
2. Find your user
3. Verify the fields were updated (bio, location, career_interests, etc.)

---

### Step 7: Test Admin Access (If You're a Director)

Since you used `SUPER_OPS_2025`, you should have admin access:

1. **Check for Admin link:**
   - In the navigation bar, you should see an "Admin" link
   - ✅ If you see it, your director check is working!

2. **Click Admin (future test):**
   - This will be implemented in Phase 6
   - For now, it will show a 404

---

### Step 8: Test Logout

1. **Click "Logout" in the navigation**

**Expected Result:**
- ✅ Redirected to `login.html`
- ✅ Local storage cleared (check Application tab in dev tools)

---

## Testing Checklist

### ✅ Backend Tests
- [ ] Backend server starts without errors
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] Configuration validated successfully

### ✅ Authentication Tests
- [ ] Signup with valid referral code succeeds
- [ ] Signup with invalid referral code fails (try "WRONG_CODE")
- [ ] Login with correct credentials succeeds
- [ ] Login with wrong password fails
- [ ] JWT token stored in localStorage
- [ ] Logout clears token and redirects to login

### ✅ Profile Editor Tests
- [ ] Profile page loads user data
- [ ] Live preview updates as you type
- [ ] Profile initials show if no profile picture
- [ ] Save button updates profile in database
- [ ] Success message appears after save
- [ ] Cancel button reverts changes
- [ ] Required fields validation (try submitting empty name)

### ✅ Navigation Tests
- [ ] Login page redirects to home after successful login
- [ ] Protected pages redirect to login if not authenticated
- [ ] Admin link only shows for directors
- [ ] All navigation links work

---

## Common Issues & Solutions

### Issue: "Network error" in frontend
**Solution:**
- Check that backend is running on port 5001
- Check browser console for CORS errors
- Make sure `API_BASE_URL` in auth.js is `http://localhost:5001`

### Issue: "Invalid referral code"
**Solution:**
- Use `LAUNCH_2025`, `OPS`, or `SUPER_OPS_2025`
- Or check your Supabase `platform_settings` table for the active code

### Issue: "Profile not found"
**Solution:**
- Make sure you completed signup
- Check Supabase that your user exists in `user_profiles` table
- Try logging out and logging back in

### Issue: Changes don't save
**Solution:**
- Check backend terminal for error messages
- Check browser console for 401 (unauthorized) errors
- Verify your JWT token exists in localStorage
- Check Supabase RLS policies are set up correctly

### Issue: Backend won't start
**Solution:**
```bash
# Make sure you're in the venv
cd /path/to/THINKInternalProject
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt

# Try running again
cd backend
python app.py
```

---

## Advanced Testing

### Test Resume Upload (Future)

1. Create a sample resume PDF
2. In signup Step 2, upload the PDF
3. **Expected:** Gemini AI parses it and pre-fills your profile
4. Check backend logs for Gemini API calls

### Test with Multiple Users

1. Sign up 2-3 test users
2. Log in as each one
3. Edit their profiles differently
4. Verify data doesn't mix between users

### Test Session Expiry

1. Log in
2. Wait for token to expire (or manually delete it from localStorage)
3. Try to access profile page
4. **Expected:** Redirected to login

---

## What to Look For

### ✅ Good Signs
- No errors in backend terminal
- No red errors in browser console
- Smooth page transitions
- Data persists after refresh
- Live preview updates instantly

### ❌ Red Flags
- 401 Unauthorized errors (auth problem)
- 500 Internal Server errors (backend bug)
- CORS errors (backend not running or wrong URL)
- Data not saving (Supabase connection issue)
- Blank profile page (profile not created)

---

## Next Steps After Testing

Once everything works:

1. **Create a few test users** with different profiles
2. **Upload different resumes** to test AI parsing
3. **Ready for Phase 3!** - AI Matching & Networking Home

See PLAN.md for what we're building next!

---

**Happy Testing! 🚀**

If you encounter issues, check:
1. Backend terminal output
2. Browser console (F12)
3. Supabase dashboard
4. This troubleshooting guide
