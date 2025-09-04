# 🚀 **QUICK START GUIDE**

## **Step 1: Install Dependencies**

```bash
cd frontend
npm install
```

**If you get errors, try:**
```bash
npm install --force
```

## **Step 2: Start Development**

### **Terminal 1 - Backend:**
```bash
cd backend
py app.py
```
**Wait for:** `✅ AI Pipeline initialized successfully!`

### **Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
**Wait for:** `Local: http://localhost:3000/`

## **Step 3: Test Integration**
1. **Open:** http://localhost:3000
2. **Look for:** Green status "Connected to AI backend"
3. **Upload:** An image and select object type
4. **Test:** Real AI processing!

## **🔧 Troubleshooting**

### **"Cannot find module 'react'"**
```bash
npm install --force
```

### **"CORS error"**
- Make sure backend is running on port 5000
- Check browser console for details

### **"Unable to connect to backend"**
- Verify backend is running: `py app.py`
- Check backend shows: `✅ AI Pipeline initialized successfully!`

### **Build/TypeScript errors**
```bash
npm run type-check
```

## **✅ Success Indicators**
- **Green connection dot** on page load
- **9 object types** in dropdown
- **Real processing times** in results
- **Working corrections** save to database
