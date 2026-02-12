# Visual Description Badge - Manual Test Cases

## Test Environment
- Backend running on http://localhost:12398
- Frontend dev server on http://localhost:5173
- Test record with at least 1 cover image and 2+ content images

## Test Cases

### TC1: Initial State - No Badges
**Steps:**
1. Open AnalyzeConfirmModal for a new record
2. Observe the image selection area

**Expected:**
- All images display without badges
- Image checkboxes work normally

### TC2: Generate Description - Badge Appears
**Steps:**
1. Select cover image and 1 content image
2. Click "生成视觉描述" (Generate Visual Description)
3. Wait for generation to complete
4. Observe selected images

**Expected:**
- Green ✓ badge appears on selected images
- Badge shows tooltip "描述已生成" on hover
- Description text appears in form with ID marker `<!-- DESC-xxx -->`

### TC3: Save Draft and Reload
**Steps:**
1. Generate descriptions for images
2. Click "保存草稿" (Save Draft)
3. Close modal
4. Re-open AnalyzeConfirmModal for same record

**Expected:**
- Badges are restored correctly
- Green ✓ on images with descriptions
- Description content is in the form

### TC4: Edit Description - Badge Changes
**Steps:**
1. Generate description for an image (should have green badge)
2. In the form, manually delete the description text (including ID marker)
3. Observe the badge

**Expected:**
- Badge changes from green ✓ to orange ⚠️
- Tooltip shows "描述内容已缺失，建议重新生成"

### TC5: Regenerate Description - Badge Restored
**Steps:**
1. Have an image with orange ⚠️ badge (missing description)
2. Select that image
3. Generate new description
4. Observe the badge

**Expected:**
- Badge changes back to green ✓
- New description appears in form

### TC6: Multiple Images Share Description
**Steps:**
1. Select 2+ content images
2. Generate description
3. Observe all selected images

**Expected:**
- All selected images get green ✓ badge
- All images share same description ID
- Badges update in sync

### TC7: Clear Form - Badges Cleared
**Steps:**
1. Generate descriptions
2. Close and reopen modal with new record (not draft)
3. Observe badges

**Expected:**
- All badges are removed
- `imageDescriptions` is empty

### TC8: API Failure - No Badge Update
**Steps:**
1. Disconnect backend or simulate API failure
2. Select images and generate description
3. Observe behavior

**Expected:**
- Error message shown
- No badges added
- `imageDescriptions` unchanged

### TC9: Cover Image Index -1
**Steps:**
1. Generate description for cover image only
2. Check badge state

**Expected:**
- Cover image has badge with index -1
- Badge works same as content images

### TC10: Persist Across Sessions
**Steps:**
1. Generate descriptions, save draft
2. Refresh browser page
3. Re-open modal

**Expected:**
- All badges correctly restored
- Description content present
