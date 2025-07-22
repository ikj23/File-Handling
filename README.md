📁 File Organizer

A lightweight, intelligent file management system that automatically organizes files into categorized folders with real-time monitoring, scheduled cleanup, and an intuitive GUI interface.

✨ Features

- 🔍 Real-time File Monitoring**: Automatically detects and organizes new files as they're created
- 🎛️ Simple GUI Configuration**: Easy-to-use interface for setting up file organization rules
- 📅 Scheduled Cleanup**: Periodically removes old files at configurable intervals
- 🗑️ Auto-cleanup**: Automatically deletes files older than specified days
- 📝 Comprehensive Logging**: Detailed logs of all file operations with timestamps
- ⚙️ Customizable Rules**: Define your own file categories and extensions
- 🔄 Smart Duplicate Handling**: Intelligent renaming for files with duplicate names
- 💾 Persistent Settings**: Saves your preferences across sessions
- ⚡ Lightweight**: No external dependencies beyond standard Python libraries

🚀 Quick Start

### Prerequisites

```bash
pip install watchdog schedule
```

### Installation & Usage

1. **Download the script**
   ```bash
   #clone the repository
   git clone <repository-url>
   cd File-Handling
   cd main
   ```

2. **Run the application**
   ```bash
   python 1.py
   ```

3. **Select folder to organize**
   - A dialog will automatically prompt you to choose the folder you want to monitor
   - **Important**: Select a folder you want to keep organized (e.g., Downloads, Desktop)

4. **Configure organization rules**
   - The GUI opens with pre-configured categories
   - Add/modify categories and their file extensions
   - Configure scheduler and auto-delete settings
   - Click "✅ Save & Start Organizer" to begin

5. **Monitor in background**
   - The application runs in your terminal
   - Press `Ctrl+C` to stop monitoring

# 🎛️ Configuration

### Default File Categories

The system comes with these pre-configured categories:

| Category | Extensions | Example Files |
|----------|------------|---------------|
| **PDFs** | `.pdf` | documents, reports, manuals |
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif` | photos, screenshots, graphics |
| **Videos** | `.mp4`, `.mkv`, `.avi` | movies, clips, recordings |
| **Word** | `.docx`, `.pptx` | documents, presentations |
| **Data** | `.csv` | spreadsheets, data files |

### Scheduler Settings

- **⏱ Scheduler Enabled**: Toggle automatic periodic cleanup
- **Interval**: Set how often to run cleanup tasks (in hours)
- **🧹 Auto-Delete Enabled**: Enable automatic removal of old files
- **Delete After**: Number of days before files are automatically deleted

### Custom Categories

Easily add your own file types:

```
📁 Folder Name: Music
➕ Extensions: .mp3, .wav, .flac, .aac

📁 Folder Name: Archives  
➕ Extensions: .zip, .rar, .7z, .tar

📁 Folder Name: Code
➕ Extensions: .py, .js, .html, .css
```

## 🔧 How It Works

### Initial Organization
1. **Folder Selection**: Choose any folder you want to keep organized
2. **Immediate Sort**: All existing files are organized into appropriate subfolders
3. **Folder Creation**: Creates category folders (PDFs/, Images/, etc.) automatically

### Real-time Monitoring
1. **File Detection**: Uses `watchdog` to detect new files instantly
2. **Smart Categorization**: Matches file extensions to your rules
3. **Duplicate Handling**: Automatically renames duplicates (e.g., `document(1).pdf`)
4. **Logging**: Records every action with timestamps

### Scheduled Cleanup (Optional)
1. **Configurable Intervals**: Run cleanup every N hours
2. **Age-based Deletion**: Remove files older than specified days
3. **Safe Operation**: Only deletes files in organized subfolders

## 📝 Logging System

All operations are logged with detailed timestamps:

```
2025-01-15 14:30:25,123 - INFO - Moved 'document.pdf' to 'PDFs'
2025-01-15 14:31:10,456 - INFO - Moved 'photo.jpg' to 'Images'  
2025-01-15 15:00:00,789 - INFO - [AUTO-DELETE] Deleting: old_file.txt (last modified: 2024-12-15 10:30:25)
2025-01-15 15:05:15,234 - INFO - Left 'unknown_file.xyz' (no matching rule)
```

## ⚙️ Advanced Usage

### Custom File Categories

1. **Add Category**: Enter folder name and extensions in GUI
2. **Multiple Extensions**: Separate with commas (`.mp3, .wav, .flac`)
3. **Case Insensitive**: Extensions work regardless of case (`.PDF` = `.pdf`)
4. **Instant Updates**: Changes apply immediately after saving

### Scheduler Configuration

```
⏱ Scheduler Enabled: ✓
Interval (hours): 6           # Clean up every 6 hours
🧹 Auto-Delete Enabled: ✓
Delete after (days): 30       # Remove files older than 30 days
```

### Safe Auto-Delete

- **Only affects organized files**: Files in category folders (PDFs/, Images/, etc.)
- **Preserves root files**: Files in the main watched folder are never auto-deleted
- **Configurable retention**: Set any number of days before deletion
- **Logged operations**: Every deletion is recorded with timestamps

## 🚨 Important Safety Notes

- **⚠️ Test First**: Always test with non-critical files initially
- **💾 Backup Important Data**: Backup valuable files before enabling auto-delete
- **🔍 Check Logs**: Monitor `file_organizer_log.txt` for all operations
- **⏸️ Easy Stop**: Press `Ctrl+C` anytime to stop the organizer
- **📁 Root Safety**: Files in the main folder are only moved, never deleted by scheduler

## 🎯 Use Cases

### Perfect For:
- **Downloads Folder**: Keep downloads organized automatically
- **Desktop Cleanup**: Sort desktop files into neat categories  
- **Work Documents**: Organize incoming files by type
- **Media Collections**: Separate photos, videos, and music
- **Development Projects**: Sort code files, assets, and documentation

### Example Workflows:

**Student Setup:**
```
📁 Assignments: .docx, .pptx, .pdf
📁 Research: .pdf, .txt, .md
📁 Code: .py, .java, .cpp
📁 Media: .jpg, .png, .mp4
```

**Designer Setup:**
```
📁 Graphics: .psd, .ai, .svg
📁 Photos: .jpg, .png, .tiff
📁 Assets: .pdf, .eps, .indd
📁 Exports: .jpg, .png, .pdf
```

## 🛠️ Troubleshooting

### Common Issues

**Files Not Moving:**
- Check file extensions match your rules exactly
- Ensure you have write permissions for the folder
- Look at logs for "no matching rule" messages

**Permission Errors:**
- Run as administrator on Windows
- Check folder permissions on macOS/Linux
- Ensure the folder isn't read-only

**GUI Doesn't Appear:**
- Ensure `tkinter` is installed (usually comes with Python)
- Try running with `python -m tkinter` to test GUI support

**Scheduler Not Working:**
- Check "Scheduler Enabled" is checked
- Verify interval is set to a reasonable number (1-24 hours)
- Look for scheduler messages in the logs

### System Requirements

- **Python**: 3.6 or higher
- **GUI Library**: tkinter (usually included with Python)
- **Required Packages**: 
  ```bash
  pip install watchdog schedule
  ```
- **Operating System**: Windows, macOS, or Linux
- **Permissions**: Read/write access to the target folder

## 🔧 Technical Details

### Architecture
- **File Monitoring**: Uses `watchdog` library for efficient file system events
- **GUI Framework**: Built with `tkinter` for cross-platform compatibility
- **Configuration**: JSON-based settings for easy modification
- **Logging**: Python's built-in `logging` module for comprehensive tracking
- **Threading**: Background scheduler runs in separate daemon thread

### Performance
- **Minimal CPU Usage**: Only processes when files are added
- **Memory Efficient**: Small memory footprint, suitable for long-term running
- **Fast Response**: Files are organized within seconds of creation

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
   ```bash
   git commit -m 'Add support for .xyz file type'
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Ideas for Contributions
- Support for nested folder organization
- Integration with cloud storage services
- Web-based configuration interface
- More sophisticated file type detection
- Statistics and analytics features
- Dark mode GUI theme

## 🔮 Roadmap

### Planned Features
- [ ] **Web Dashboard**: Browser-based configuration and monitoring
- [ ] **Rule Templates**: Pre-built organization templates for different use cases
- [ ] **Cloud Integration**: Support for Dropbox, Google Drive, OneDrive
- [ ] **Advanced Filtering**: Organization based on file size, date, or content
- [ ] **Statistics Dashboard**: Visual insights into your file organization
- [ ] **Mobile App**: Remote monitoring and control
- [ ] **Batch Operations**: Bulk file operations and undo functionality

### Version History
- **v1.0**: Initial release with basic organization
- **v2.0**: Added GUI configuration and scheduler
- **v2.1**: Improved duplicate handling and logging
- **Current**: Streamlined architecture, enhanced safety features

---

**Made with ❤️ for better file organization**

**⚠️ Always backup important files before using auto-delete features**
