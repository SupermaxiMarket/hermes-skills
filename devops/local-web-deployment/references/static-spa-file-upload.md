# File Upload in Static SPAs (no backend)

When building a self-contained HTML artifact that needs file upload but has **no backend server**.

## Architecture

```
<input type="file"> → FileReader.readAsDataURL() → base64 string → localStorage
                                                                        ↓
                                                              <img>/<iframe> src
```

Files live entirely in the browser. No server receives them.

## Key Constraints

| Factor | Limit | Why |
|--------|-------|-----|
| Single file | **5 MB max** | localStorage quota is typically 5-10 MB per origin |
| Total storage | ~5 MB origin limit | All docs + metadata share this space |
| Portability | Origin-locked | Data stays in the browser that created it |

## Implementation

### HTML
```html
<div id="upload-area" onclick="document.getElementById('file-input').click()">
  <input type="file" id="file-input" accept=".pdf,.jpg,.png" style="display:none"
         onchange="handleFile(event)">
</div>
```

### JS: Read file
```javascript
function handleFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) { alert('Max 5 Mo'); return; }

  const reader = new FileReader();
  reader.onload = function(e) {
    saveItem(file.name, file.type, e.target.result); // base64 data URL
  };
  reader.readAsDataURL(file);
}
```

### JS: View in new tab
```javascript
function viewFile(index) {
  const doc = items[index];
  const w = window.open('', '_blank');
  w.document.write('<html><head><title>' + doc.title + '</title></head><body>');
  if (doc.fileType?.startsWith('image/'))
    w.document.write('<img src="' + doc.fileData + '" style="max-width:100%">');
  else
    w.document.write('<iframe src="' + doc.fileData + '" style="width:100%;height:100vh;border:none;"></iframe>');
  w.document.write('</body></html>');
  w.document.close();
}
```

## Async Pitfall

`FileReader.readAsDataURL()` is **async**:

```javascript
// ❌ WRONG — items.push runs before reader fires
const reader = new FileReader();
reader.readAsDataURL(file);
items.push({ fileData: reader.result }); // undefined!

// ✅ CORRECT — push inside onload
reader.onload = function(e) {
  items.push({ fileData: e.target.result });
  saveAndRender();
};
reader.readAsDataURL(file);
```

## When NOT to use

- More than a handful of files (localStorage fills fast)
- Large PDFs, videos (base64 adds ~33% overhead)
- Cross-device access needed (data is origin-scoped)
- User expects real cloud backup (there is none)

For those cases, the SPA needs a real backend (upload endpoint + object storage).

## Visual Feedback

```javascript
function handleFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  document.getElementById('file-name-display').textContent =
    '✓ ' + file.name + ' (' + (file.size / 1024).toFixed(1) + ' Ko)';
  document.getElementById('file-name-display').style.display = 'block';
  document.getElementById('upload-area').style.borderColor = '#27a644';
  document.getElementById('upload-area').style.background = 'rgba(39,166,68,0.05)';
}
```