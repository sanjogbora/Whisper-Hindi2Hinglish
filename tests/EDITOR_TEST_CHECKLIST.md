# Editor Integration Test Checklist

This document provides a manual testing checklist for verifying the editor interface integration with the backend APIs.

## Test Environment Setup

- [ ] Backend server is running (`python web_server.py`)
- [ ] Server is accessible at `http://localhost:5000`
- [ ] Frontend editor files are in `templates/` directory
- [ ] Test video file is available for upload

---

## UI Component Tests

### Page Loading

- [ ] **Editor page loads without errors**
  - Navigate to `http://localhost:5000/editor`
  - Verify page loads and displays correctly
  - Check browser console for no JavaScript errors

- [ ] **Sessions list page loads**
  - Navigate to `http://localhost:5000/sessions`
  - Verify page displays list of sessions
  - Check table/grid layout is correct

- [ ] **Upload page loads**
  - Navigate to `http://localhost:5000/upload-page`
  - Verify upload form is displayed
  - Check file input and model selection options

### Video Player Controls

- [ ] **Video player displays**
  - Upload a video and navigate to editor
  - Verify video player element is visible
  - Check video thumbnail/poster loads

- [ ] **Play/Pause controls work**
  - Click play button
  - Verify video starts playing
  - Click pause button
  - Verify video pauses

- [ ] **Seek controls work**
  - Drag timeline scrubber
  - Verify video jumps to new position
  - Click on timeline bar
  - Verify video seeks to clicked position

- [ ] **Volume controls work**
  - Adjust volume slider
  - Verify audio level changes
  - Mute/unmute button works

### Timeline Display

- [ ] **Timeline displays frames**
  - Verify timeline shows frame thumbnails
  - Check frame captions are displayed
  - Verify timeline represents video duration

- [ ] **Timeline is interactive**
  - Click on timeline to seek
  - Hover over frames shows preview
  - Current position indicator moves during playback

### Style Controls

- [ ] **Style controls render correctly**
  - Verify preset dropdown is visible
  - Check custom style options are displayed
  - Verify font selection works

- [ ] **Preset dropdown loads presets**
  - Click preset dropdown
  - Verify all 5 presets are listed
  - Check "reels_standard" is default

- [ ] **Custom style controls work**
  - Adjust font size slider
  - Change color picker
  - Toggle bold/italic options
  - Verify preview updates

### Upload Interface

- [ ] **File upload dialog works**
  - Click upload button/select file
  - Verify file dialog opens
  - Select video/audio file
  - Verify file name displays

- [ ] **Model selection works**
  - Select "prime" model
  - Select "swift" model
  - Verify selection persists

- [ ] **Upload progress shows**
  - Start upload
  - Verify progress bar appears
  - Check percentage updates
  - Verify completion message

---

## API Integration Tests

### Session Creation

- [ ] **Can create session from editor**
  - Upload video via editor
  - Verify session is created
  - Check session_id is returned
  - Verify redirect to editor with session

- [ ] **Session status updates correctly**
  - Upload video
  - Check status changes: created → processing → transcribed
  - Verify status displays in UI

- [ ] **Error handling for invalid file**
  - Upload non-media file (e.g., .txt)
  - Verify error message displays
  - Check no session is created

### Session Retrieval

- [ ] **Can fetch session data**
  - Load editor with session_id
  - Verify session data loads
  - Check video path is valid
  - Verify captions path is set

- [ ] **Session list loads correctly**
  - Navigate to sessions page
  - Verify all sessions are listed
  - Check session details display (ID, status, date)
  - Verify pagination if many sessions

### Caption Style Application

- [ ] **Can apply style changes**
  - Select different preset
  - Verify style is applied
  - Check preview updates
  - Verify session metadata updated

- [ ] **Custom style overrides work**
  - Modify font size
  - Change color
  - Apply custom style
  - Verify changes persist

- [ ] **Style preview updates**
  - Apply different styles
  - Check preview reflects style
  - Verify captions display correctly
  - Check font rendering

### Preview Generation

- [ ] **Can generate preview**
  - Click "Generate Preview" button
  - Verify frames are generated
  - Check preview displays in timeline
  - Verify captions are burned into frames

- [ ] **Preview parameters work**
  - Change FPS setting
  - Adjust max frames
  - Generate preview
  - Verify correct number of frames

- [ ] **Preview displays captions**
  - Check captions are visible in frames
  - Verify text positioning is correct
  - Check font rendering quality
  - Verify color and outline

### Caption Embedding

- [ ] **Can embed captions**
  - Apply style to session
  - Click "Embed Captions" button
  - Verify embedding starts
  - Check progress indicator

- [ ] **Output video is created**
  - Wait for embedding to complete
  - Verify output file exists
  - Check file is downloadable
  - Verify video plays with captions

- [ ] **Embedding options work**
  - Test with burn=true
  - Test with burn=false
  - Verify different outputs

### Error Messages Display

- [ ] **Upload errors show correctly**
  - Upload invalid file
  - Verify error message is clear
  - Check error message includes details
  - Verify user can retry

- [ ] **API errors show correctly**
  - Simulate API failure
  - Verify error message displays
  - Check error is logged
  - Verify user can continue

- [ ] **Network errors handled**
  - Disconnect network during operation
  - Verify error message shows
  - Check operation can be retried
  - Verify no data corruption

---

## Workflow Tests

### Complete Workflow Test

- [ ] **Upload → Edit Style → Preview → Embed**
  1. Upload video file
  2. Wait for transcription to complete
  3. Navigate to editor
  4. Apply "reels_standard" preset
  5. Generate preview frames
  6. Verify captions in preview
  7. Adjust style if needed
  8. Embed captions into video
  9. Download output video
  10. Verify output plays correctly

### Multi-Session Workflow

- [ ] **Can work with multiple sessions**
  1. Create Session A with video 1
  2. Create Session B with video 2
  3. Navigate between sessions
  4. Apply different styles to each
  5. Generate previews for both
  6. Embed captions for both
  7. Verify both outputs are correct

### Session Management

- [ ] **Can delete sessions**
  1. Create a session
  2. Go to sessions list
  3. Click delete button
  4. Confirm deletion
  5. Verify session is removed
  6. Check files are cleaned up

- [ ] **Can clone session style**
  1. Configure style in Session A
  2. Create Session B
  3. Apply same style from A to B
  4. Verify styles match

---

## Keyboard Shortcuts

- [ ] **Space key plays/pauses**
  - Press Space while video loaded
  - Verify play/pause toggles

- [ ] **Arrow keys seek video**
  - Press Left Arrow
  - Verify video seeks backward
  - Press Right Arrow
  - Verify video seeks forward

- [ ] **F key toggles fullscreen**
  - Press F key
  - Verify video enters fullscreen
  - Press F again
  - Verify video exits fullscreen

- [ ] **Escape key exits fullscreen**
  - Enter fullscreen
  - Press Escape
  - Verify video exits fullscreen

---

## User Feedback

### Toast Notifications

- [ ] **Toast notifications appear**
  - Upload completes
  - Verify success toast appears
  - Check toast auto-dismisses

- [ ] **Error toasts appear**
  - Operation fails
  - Verify error toast appears
  - Check toast shows error details

- [ ] **Progress toasts appear**
  - Long-running operation starts
  - Verify progress toast shows
  - Check percentage updates

### Progress Bars

- [ ] **Upload progress bar updates**
  - Start upload
  - Verify progress bar appears
  - Check percentage updates smoothly
  - Verify bar completes at 100%

- [ ] **Processing progress bar updates**
  - Start transcription
  - Verify progress bar shows
  - Check status text updates
  - Verify bar completes

- [ ] **Embedding progress bar updates**
  - Start embedding
  - Verify progress bar shows
  - Check percentage updates
  - Verify bar completes

### Loading States

- [ ] **Loading spinners appear**
  - Page is loading
  - Verify spinner shows
  - Check spinner disappears when ready

- [ ] **Button states change during processing**
  - Click "Embed Captions"
  - Verify button is disabled
  - Check button shows "Processing..."
  - Verify button re-enables when complete

---

## Browser Compatibility

- [ ] **Chrome/Edge**
  - Test all features in Chrome
  - Test all features in Edge

- [ ] **Firefox**
  - Test all features in Firefox
  - Verify consistent behavior

- [ ] **Safari** (if available)
  - Test all features in Safari
  - Verify consistent behavior

---

## Performance Tests

- [ ] **Large file upload**
  - Upload 100MB+ video
  - Verify upload completes
  - Check UI remains responsive

- [ ] **Long video processing**
  - Upload 10+ minute video
  - Verify transcription completes
  - Check progress updates

- [ ] **Multiple concurrent sessions**
  - Create 3+ sessions
  - Verify all process correctly
  - Check UI remains responsive

---

## Edge Cases

- [ ] **Empty video file**
  - Upload 0-byte file
  - Verify error message

- [ ] **Corrupted video file**
  - Upload corrupted video
  - Verify error handling

- [ ] **Very short video**
  - Upload < 1 second video
  - Verify processing works

- [ ] **Very long video**
  - Upload > 1 hour video
  - Verify processing works

- [ ] **No captions generated**
  - Upload silent video
  - Verify empty SRT is handled

- [ ] **Special characters in filename**
  - Upload file with special chars
  - Verify filename is handled

- [ ] **Unicode characters in filename**
  - Upload file with Unicode chars
  - Verify filename is handled

---

## Accessibility

- [ ] **Keyboard navigation works**
  - Tab through all controls
  - Verify focus indicators visible
  - Check all elements reachable

- [ ] **Screen reader compatibility**
  - Test with screen reader
  - Verify labels are read
  - Check alt text is present

- [ ] **Color contrast**
  - Verify text contrast meets WCAG
  - Check color-blind friendly colors

---

## Test Results Summary

### Tests Passed: ___ / ___
### Tests Failed: ___ / ___
### Tests Skipped: ___ / ___

### Issues Found:

1. ___________________________________________________________

2. ___________________________________________________________

3. ___________________________________________________________

### Recommendations:

1. ___________________________________________________________

2. ___________________________________________________________

3. ___________________________________________________________

---

## Notes

- Date tested: ________________________
- Tester: ________________________
- Browser version: ________________________
- OS version: ________________________
- Server version: ________________________