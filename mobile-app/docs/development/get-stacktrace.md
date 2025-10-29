# How to Get the Full Stacktrace

## To get the exact error:

1. **In Android Studio:**
   - Look at the "Build" tab at the bottom
   - Copy the full error message (scroll to see all of it)

2. **OR run from terminal:**
   ```bash
   cd /path/to/mobile-app
   ./gradlew build --stacktrace
   ```

3. **Copy the entire error output** and share it

The error message should show exactly which dependency is causing the `.module()` issue.

---

**Please share the full error message from the "Build" output in Android Studio.**


